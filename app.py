import sys
import os
import threading
import time
import numpy as np
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Correct sys.path for src import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Corrected imports (underscore style)
from src.network.topologysetup import NetworkTopology
from src.algorithms.backpressure_routing import BackpressureRouter
from src.algorithms.tcp_congestion import TCPCongestionControl
from src.algorithms.ml_predicter import CongestionPredictor

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
app.config['SECRET_KEY'] = 'cn_project_2025'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

network = None
router = None
tcp = None
ml_predictor = None
simulation_running = False
simulation_thread = None
previous_queue_length = 0
previous_cwnd = 1


def create_network():
    global network, router, tcp, ml_predictor, previous_queue_length, previous_cwnd
    network = NetworkTopology(
        num_iot_devices=5,
        num_edge_nodes=2,
        num_fog_nodes=3,
        num_cloud_nodes=1
    )
    network.create_topology()
    router = BackpressureRouter(network)
    tcp = TCPCongestionControl(network, initial_cwnd=1, ssthresh=16)
    ml_predictor = CongestionPredictor(history_window=10, prediction_horizon=2)
    previous_queue_length = 0
    previous_cwnd = 1
    print("✓ Network created successfully")
    print("✓ ML Predictor initialized")
    return network


def get_network_data():
    if not network:
        return {}
    nodes = []
    edges = []
    layer_positions = {'iot': 0, 'edge': 2, 'fog': 4, 'cloud': 6}
    layer_counts = {'iot': 0, 'edge': 0, 'fog': 0, 'cloud': 0}
    for node in network.graph.nodes():
        layer = network.graph.nodes[node].get('layer', 'iot')
        layer_counts[layer] += 1
        nodes.append({
            'id': node,
            'label': node,
            'layer': layer,
            'x': layer_counts[layer] * 100,
            'y': layer_positions[layer] * 100,
            'queue': network.node_queues.get(node, 0)
        })
    for edge in network.graph.edges():
        edges.append({
            'from': edge[0],
            'to': edge[1],
            'bandwidth': network.link_bandwidths.get(edge, 10)
        })
    return {'nodes': nodes, 'edges': edges}


def simulation_worker():
    global simulation_running, previous_queue_length, previous_cwnd
    print("\n Simulation worker started with ML prediction!")
    round_num = 0
    while simulation_running:
        round_num += 1
        print(f"\n--- Round {round_num} ---")
        try:
            source = network.iot_nodes[round_num % len(network.iot_nodes)]
            if round_num % 3 == 0:
                dest = network.cloud_nodes[0]
            else:
                dest = network.fog_nodes[round_num % len(network.fog_nodes)]
            result = router.route_task(f"Task_{round_num}", source, dest, task_size=1)
            print(f"  Routed: {result['task_id']} - {result['status']}")
            bp_success_rate = (router.successful_routes / router.total_tasks_routed * 100) if router.total_tasks_routed > 0 else 0
            successful_hops = [r['hops'] for r in router.routing_decisions if r['status'] == 'SUCCESS']
            bp_avg_hops = sum(successful_hops) / len(successful_hops) if successful_hops else 0
            bp_metrics = {
                'success_rate': bp_success_rate,
                'total_tasks': router.total_tasks_routed,
                'avg_hops': bp_avg_hops,
                'total_queue_load': sum(network.node_queues.values())
            }
            socketio.emit('routing_update', {
                'task_id': result['task_id'],
                'path': result['path'],
                'status': result['status'],
                'hops': result['hops']
            })
            socketio.emit('bp_metrics_update', bp_metrics)
            tasks_to_send = int(tcp.cwnd)
            congestion_detected = tcp.detect_congestion()
            queue_lengths = [network.node_queues.get(node, 0) for node in network.edge_nodes + network.fog_nodes]
            avg_queue = np.mean(queue_lengths) if queue_lengths else 0
            max_queue = max(queue_lengths) if queue_lengths else 0
            queue_growth_rate = avg_queue - previous_queue_length
            cwnd_growth_rate = tcp.cwnd - previous_cwnd
            network_state = {
                'avg_queue_length': avg_queue,
                'max_queue_length': max_queue,
                'cwnd': tcp.cwnd,
                'recent_packet_losses': tcp.packet_loss_events,
                'throughput': tasks_to_send,
                'queue_growth_rate': queue_growth_rate,
                'cwnd_growth_rate': cwnd_growth_rate
            }
            ml_predictor.collect_training_data(network_state, congestion_detected)
            prediction_result = ml_predictor.predict_congestion(network_state)
            ml_predictor.update_prediction_accuracy(congestion_detected)
            ml_stats = ml_predictor.get_statistics()
            print(f"  ML Prediction: {prediction_result['prediction']} ({prediction_result['confidence']:.1f}% confidence)")
            print(f"  ML Accuracy: {ml_stats['accuracy']:.1f}%")
            socketio.emit('ml_prediction', {
                'prediction': prediction_result['prediction'],
                'confidence': prediction_result['confidence'],
                'status': prediction_result['status'],
                'accuracy': ml_stats['accuracy'],
                'is_trained': ml_stats['is_trained'],
                'training_samples': ml_stats['training_samples']
            })
            previous_queue_length = avg_queue
            previous_cwnd = tcp.cwnd
            if congestion_detected:
                tcp.handle_packet_loss()
                print(f"  TCP: Packet loss! CWND={tcp.cwnd:.2f}")
            else:
                tcp.successful_transmissions += tasks_to_send
                tcp.total_packets_sent += tasks_to_send
                if tcp.state == tcp.SLOW_START:
                    tcp.slow_start_phase()
                else:
                    tcp.congestion_avoidance_phase()
                print(f"  TCP: CWND={tcp.cwnd:.2f}, State={tcp.state}")
            tcp.cwnd_history.append(tcp.cwnd)
            socketio.emit('tcp_update', {
                'round': round_num,
                'cwnd': tcp.cwnd,
                'ssthresh': tcp.ssthresh,
                'state': tcp.state,
                'congestion': congestion_detected,
                'losses': tcp.packet_loss_events
            })
            socketio.emit('network_update', {
                'queues': network.node_queues,
                'total_queue': sum(network.node_queues.values())
            })
        except Exception as e:
            print(f"  ERROR in simulation: {e}")
            import traceback
            traceback.print_exc()
        time.sleep(1.5)
    print("\n Simulation worker stopped")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/network')
def get_network():
    if not network:
        create_network()
    return jsonify(get_network_data())

@app.route('/api/metrics')
def get_metrics():
    if not router or not tcp:
        return jsonify({})
    bp_metrics = router.get_performance_metrics() if router.total_tasks_routed > 0 else {}
    tcp_metrics = tcp.get_performance_metrics() if tcp.total_packets_sent > 0 else {}
    return jsonify({ 'backpressure': bp_metrics, 'tcp': tcp_metrics })

@socketio.on('connect')
def handle_connect():
    print('✓ Client connected')
    if not network:
        create_network()
    emit('network_data', get_network_data())

@socketio.on('disconnect')
def handle_disconnect():
    print('✗ Client disconnected')

@socketio.on('start_simulation')
def handle_start_simulation():
    global simulation_running, simulation_thread
    if not simulation_running:
        simulation_running = True
        simulation_thread = threading.Thread(target=simulation_worker)
        simulation_thread.daemon = True
        simulation_thread.start()
        emit('simulation_status', {'running': True})
        print('✓ Simulation started')

@socketio.on('stop_simulation')
def handle_stop_simulation():
    global simulation_running
    simulation_running = False
    emit('simulation_status', {'running': False})
    print('✓ Simulation stopped')

@socketio.on('reset_simulation')
def handle_reset_simulation():
    global network, router, tcp, simulation_running
    simulation_running = False
    time.sleep(1)
    create_network()
    emit('simulation_status', {'running': False})
    emit('network_data', get_network_data())
    print('✓ Simulation reset')

if __name__ == '__main__':
    print("="*70)
    print("CN Healthcare Edge Computing - Real-Time Web Dashboard")
    print("WITH ML CONGESTION PREDICTION")
    print("="*70)
    print("\n Starting Flask server...")
    print(" Dashboard URL: http://localhost:5000")
    print(" Open your browser and navigate to the URL above\n")
    print("="*70)
    create_network()
    socketio.run(app, debug=False, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)