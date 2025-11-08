import random
import math
from colorama import Fore, Style, init
from tabulate import tabulate
import matplotlib.pyplot as plt

init(autoreset=True)


class TCPCongestionControl:
    """TCP Congestion Control with AIMD Algorithm"""
    
    SLOW_START = "SLOW_START"
    CONGESTION_AVOIDANCE = "CONGESTION_AVOIDANCE"
    FAST_RECOVERY = "FAST_RECOVERY"

    def __init__(self, network_topology, initial_cwnd=1, ssthresh=16):
        """Initialize TCP Congestion Control"""
        self.topology = network_topology
        self.graph = network_topology.graph
        self.node_queues = network_topology.node_queues

        self.cwnd = initial_cwnd
        self.ssthresh = ssthresh
        self.state = self.SLOW_START

        self.cwnd_history = [initial_cwnd]
        self.throughput_history = []
        self.packet_loss_events = 0
        self.total_packets_sent = 0
        self.successful_transmissions = 0
        self.rtt_samples = []

        self.max_cwnd = 64
        self.min_cwnd = 1
        self.duplicate_ack_count = 0
        self.fast_retransmit_threshold = 3

        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}TCP Congestion Control Algorithm Initialized")
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.YELLOW}Algorithm Type: Transport Layer Congestion Control")
        print(f"{Fore.YELLOW}Control Strategy: AIMD (Additive Increase Multiplicative Decrease)")
        print(f"{Fore.YELLOW}Initial CWND: {initial_cwnd} | SSThresh: {ssthresh}")
        print(f"{Fore.CYAN}{'='*70}\n")

    def detect_congestion(self):
        """Detect congestion in the network"""
        relevant_nodes = self.topology.edge_nodes + self.topology.fog_nodes

        if not relevant_nodes:
            return False

        avg_queue = sum(self.node_queues.get(node, 0) for node in relevant_nodes) / len(relevant_nodes)
        congestion_threshold = 5
        random_loss = random.random() < 0.05

        return avg_queue > congestion_threshold or random_loss

    def slow_start_phase(self):
        """Slow Start phase: exponential CWND increase"""
        old_cwnd = self.cwnd
        self.cwnd = min(self.cwnd * 2, self.max_cwnd)

        if self.cwnd >= self.ssthresh:
            self.state = self.CONGESTION_AVOIDANCE
            print(f"{Fore.YELLOW}  [TCP] Slow Start → Congestion Avoidance (cwnd={self.cwnd:.2f})")

        return self.cwnd

    def congestion_avoidance_phase(self):
        """Congestion Avoidance phase: linear CWND increase"""
        old_cwnd = self.cwnd
        self.cwnd = min(self.cwnd + (1.0 / self.cwnd), self.max_cwnd)
        return self.cwnd

    def handle_packet_loss(self):
        """Handle packet loss with multiplicative decrease"""
        self.packet_loss_events += 1

        self.ssthresh = max(self.cwnd / 2, 2)
        self.cwnd = self.min_cwnd

        old_state = self.state
        self.state = self.SLOW_START

        print(f"{Fore.RED}  [TCP] Packet Loss! {old_state} → Slow Start")
        print(f"{Fore.RED}        New cwnd={self.cwnd:.2f}, ssthresh={self.ssthresh:.2f}")

    def send_tasks_batch(self, num_rounds=30):
        """Send tasks with TCP congestion control"""
        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"{Fore.GREEN}Starting TCP Congestion Control Simulation")
        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.YELLOW}Transmission rounds: {num_rounds}")
        print(f"{Fore.YELLOW}Initial state: {self.state}\n")

        for round_num in range(1, num_rounds + 1):
            tasks_to_send = int(self.cwnd)

            print(f"{Fore.CYAN}Round {round_num:2d}: State={self.state:20s} | CWND={self.cwnd:6.2f} | Sending {tasks_to_send} tasks", end='')

            successful = 0
            for i in range(tasks_to_send):
                self.total_packets_sent += 1

                if self.detect_congestion():
                    print(f" {Fore.RED}[LOSS!]")
                    self.handle_packet_loss()
                    break
                else:
                    successful += 1
                    self.successful_transmissions += 1
            else:
                print(f" {Fore.GREEN}[SUCCESS]")

                if self.state == self.SLOW_START:
                    self.slow_start_phase()
                elif self.state == self.CONGESTION_AVOIDANCE:
                    self.congestion_avoidance_phase()

            self.cwnd_history.append(self.cwnd)
            throughput = successful
            self.throughput_history.append(throughput)

            rtt = random.uniform(20, 100)
            self.rtt_samples.append(rtt)

        print(f"\n{Fore.GREEN}✓ TCP simulation completed!\n")

    def get_performance_metrics(self):
        """Calculate and display performance metrics"""
        if self.total_packets_sent == 0:
            return {}

        delivery_rate = (self.successful_transmissions / self.total_packets_sent) * 100
        packet_loss_rate = (self.packet_loss_events / len(self.cwnd_history)) * 100 if self.cwnd_history else 0
        avg_throughput = sum(self.throughput_history) / len(self.throughput_history) if self.throughput_history else 0
        avg_rtt = sum(self.rtt_samples) / len(self.rtt_samples) if self.rtt_samples else 0
        max_cwnd = max(self.cwnd_history)
        avg_cwnd = sum(self.cwnd_history) / len(self.cwnd_history)

        metrics = {
            'total_packets_sent': self.total_packets_sent,
            'successful_transmissions': self.successful_transmissions,
            'packet_loss_events': self.packet_loss_events,
            'delivery_rate': delivery_rate,
            'packet_loss_rate': packet_loss_rate,
            'avg_throughput': avg_throughput,
            'avg_rtt': avg_rtt,
            'max_cwnd': max_cwnd,
            'avg_cwnd': avg_cwnd,
            'final_cwnd': self.cwnd,
            'final_ssthresh': self.ssthresh
        }

        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}TCP CONGESTION CONTROL PERFORMANCE METRICS")
        print(f"{Fore.CYAN}{'='*70}\n")

        metrics_table = [
            ['Total Packets Sent', metrics['total_packets_sent']],
            ['Successful Transmissions', f"{metrics['successful_transmissions']} ({metrics['delivery_rate']:.2f}%)"],
            ['Packet Loss Events', f"{metrics['packet_loss_events']} ({metrics['packet_loss_rate']:.2f}%)"],
            ['Average Throughput', f"{metrics['avg_throughput']:.2f} tasks/round"],
            ['Average RTT', f"{metrics['avg_rtt']:.2f} ms"],
            ['Max CWND Achieved', f"{metrics['max_cwnd']:.2f}"],
            ['Average CWND', f"{metrics['avg_cwnd']:.2f}"],
            ['Final CWND', f"{metrics['final_cwnd']:.2f}"],
            ['Final SSThresh', f"{metrics['final_ssthresh']:.2f}"]
        ]

        print(tabulate(metrics_table, headers=['Metric', 'Value'], tablefmt='grid'))
        print(f"{Fore.CYAN}{'='*70}\n")

        return metrics

    def plot_congestion_window(self, save_path=None):
        """Plot TCP congestion window evolution"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        rounds = list(range(len(self.cwnd_history)))
        ax1.plot(rounds, self.cwnd_history, 'b-', linewidth=2, label='CWND')
        ax1.axhline(y=self.ssthresh, color='r', linestyle='--', label=f'SSThresh={self.ssthresh}')
        ax1.set_xlabel('Round (RTT)', fontsize=12)
        ax1.set_ylabel('Congestion Window (CWND)', fontsize=12)
        ax1.set_title('TCP Congestion Window Evolution', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        throughput_rounds = list(range(len(self.throughput_history)))
        ax2.plot(throughput_rounds, self.throughput_history, 'g-', linewidth=2, label='Throughput')
        ax2.set_xlabel('Round (RTT)', fontsize=12)
        ax2.set_ylabel('Throughput (tasks/round)', fontsize=12)
        ax2.set_title('Task Transmission Throughput', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"{Fore.GREEN}TCP performance plot saved to: {save_path}")

        plt.show()


if __name__ == "__main__":
    import sys
    import os

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from network.topologysetup import NetworkTopology

    print(f"{Fore.MAGENTA}{'='*70}")
    print(f"{Fore.MAGENTA}TESTING TCP CONGESTION CONTROL ALGORITHM")
    print(f"{Fore.MAGENTA}{'='*70}\n")

    print(f"{Fore.YELLOW}Step 1: Creating network topology...")
    network = NetworkTopology(
        num_iot_devices=5,
        num_edge_nodes=2,
        num_fog_nodes=3,
        num_cloud_nodes=1
    )
    # FIX: Don't call create_topology() again - it's already called in _init_

    print(f"\n{Fore.YELLOW}Step 2: Initializing TCP Congestion Control...")
    tcp = TCPCongestionControl(network, initial_cwnd=1, ssthresh=16)

    print(f"\n{Fore.YELLOW}Step 3: Running TCP transmission simulation...")
    tcp.send_tasks_batch(num_rounds=30)

    metrics = tcp.get_performance_metrics()

    print(f"{Fore.YELLOW}Step 4: Generating performance plots...")
    results_dir = os.path.join(os.getcwd(), 'results', 'graphs')
    os.makedirs(results_dir, exist_ok=True)
    save_path = os.path.join(results_dir, 'tcp_congestion_control.png')
    tcp.plot_congestion_window(save_path=save_path)

    print(f"\n{Fore.GREEN}✓ TCP Congestion Control Algorithm tested successfully!\n")