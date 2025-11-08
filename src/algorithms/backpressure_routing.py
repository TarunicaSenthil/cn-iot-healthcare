import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir,'src'))
                                
import random
import math
from colorama import Fore, Style, init
from tabulate import tabulate

init(autoreset=True)


class BackpressureRouter:
    
    def __init__(self, network_topology):
        self.topology = network_topology
        self.graph = network_topology.graph
        self.node_queues = network_topology.node_queues
        self.link_bandwidths = network_topology.link_bandwidths
        
       
        self.routing_decisions = []
        self.total_tasks_routed = 0
        self.successful_routes = 0
        self.failed_routes = 0
        
       
        self.alpha = 0.6
        self.beta = 0.4
        
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}Backpressure Routing Algorithm Initialized")
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.YELLOW}Algorithm Type: Network Layer Routing Protocol")
        print(f"{Fore.YELLOW}Routing Strategy: Queue-aware distributed routing")
        print(f"{Fore.CYAN}{'='*70}\n")
        
    def calculate_backpressure(self, current_node, next_node):
       
        queue_current = self.node_queues.get(current_node, 0)
        queue_next = self.node_queues.get(next_node, 0)
        
       
        queue_differential = queue_current - queue_next
        
        
        link = (current_node, next_node)
        bandwidth = self.link_bandwidths.get(link, 10.0)
        
        
        normalized_bandwidth = min(bandwidth / 100.0, 1.0)
        
        
        backpressure = (self.alpha * queue_differential) + (self.beta * normalized_bandwidth)
        
        return max(backpressure, 0)
    
    def get_next_hop(self, source, destination, current_node):
       
        neighbors = list(self.graph.successors(current_node))
        
        if not neighbors:
            return None
        
       
        backpressure_weights = {}
        
        for neighbor in neighbors:
            
            if neighbor == source:
                continue
                
            
            bp_weight = self.calculate_backpressure(current_node, neighbor)
            backpressure_weights[neighbor] = bp_weight
        
        if not backpressure_weights:
            return None
        
        
        next_hop = max(backpressure_weights, key=backpressure_weights.get)
        
        return next_hop
    
    def route_task(self, task_id, source, destination, task_size=1):
        self.total_tasks_routed += 1
        
        
        path = [source]
        current = source
        hops = 0
        max_hops = 10
        
        
        while current != destination and hops < max_hops:
            next_hop = self.get_next_hop(source, destination, current)
            
            if next_hop is None:
                
                self.failed_routes += 1
                return {
                    'task_id': task_id,
                    'source': source,
                    'destination': destination,
                    'path': path,
                    'status': 'FAILED',
                    'hops': hops,
                    'reason': 'No available next hop'
                }
            
           
            path.append(next_hop)
            self.node_queues[next_hop] += task_size
            current = next_hop
            hops += 1
        
       
        if current == destination:
            self.successful_routes += 1
            status = 'SUCCESS'
            reason = 'Destination reached'
        else:
            self.failed_routes += 1
            status = 'FAILED'
            reason = 'Max hops exceeded'
        
        
        result = {
            'task_id': task_id,
            'source': source,
            'destination': destination,
            'path': path,
            'status': status,
            'hops': hops,
            'reason': reason
        }
        
        self.routing_decisions.append(result)
        
        return result
    
    def route_batch_tasks(self, num_tasks=20):
        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"{Fore.GREEN}Starting Backpressure Routing Simulation")
        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.YELLOW}Number of tasks: {num_tasks}")
        print(f"{Fore.YELLOW}Routing strategy: Queue-differential based\n")
        
        results = []
        
        for i in range(num_tasks):
            
            source = random.choice(self.topology.iot_nodes)
            
            
            if random.random() < 0.7: 
                destination = random.choice(self.topology.fog_nodes)
            else:
                destination = random.choice(self.topology.cloud_nodes)
            
           
            task_id = f"Task_{i+1}"
            result = self.route_task(task_id, source, destination)
            results.append(result)
            
            
            if (i + 1) % 5 == 0:
                print(f"{Fore.CYAN}  → Routed {i+1}/{num_tasks} tasks...")
        
        print(f"{Fore.GREEN}✓ Routing simulation completed!\n")
        
        return results
    
    def display_routing_table(self, results):
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}BACKPRESSURE ROUTING RESULTS")
        print(f"{Fore.CYAN}{'='*70}\n")
        
        
        table_data = []
        for result in results[:10]:
            path_str = ' → '.join(result['path'])
            if len(path_str) > 40:
                path_str = path_str[:37] + '...'
            
            status_color = Fore.GREEN if result['status'] == 'SUCCESS' else Fore.RED
            
            table_data.append([
                result['task_id'],
                result['source'],
                result['destination'],
                path_str,
                result['hops'],
                f"{status_color}{result['status']}{Style.RESET_ALL}"
            ])
        
        headers = ['Task ID', 'Source', 'Destination', 'Path', 'Hops', 'Status']
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
        
        if len(results) > 10:
            print(f"\n{Fore.YELLOW}... and {len(results) - 10} more tasks\n")
    
    def get_performance_metrics(self):
        if self.total_tasks_routed == 0:
            return {}
        
        success_rate = (self.successful_routes / self.total_tasks_routed) * 100
        failure_rate = (self.failed_routes / self.total_tasks_routed) * 100
        
        
        successful_hops = [r['hops'] for r in self.routing_decisions 
                          if r['status'] == 'SUCCESS']
        avg_hops = sum(successful_hops) / len(successful_hops) if successful_hops else 0
        
        
        total_queue_load = sum(self.node_queues.values())
        
        metrics = {
            'total_tasks': self.total_tasks_routed,
            'successful_routes': self.successful_routes,
            'failed_routes': self.failed_routes,
            'success_rate': success_rate,
            'failure_rate': failure_rate,
            'avg_hops': avg_hops,
            'total_queue_load': total_queue_load
        }
        
        
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}BACKPRESSURE ROUTING PERFORMANCE METRICS")
        print(f"{Fore.CYAN}{'='*70}\n")
        
        metrics_table = [
            ['Total Tasks Routed', metrics['total_tasks']],
            ['Successful Routes', f"{metrics['successful_routes']} ({metrics['success_rate']:.2f}%)"],
            ['Failed Routes', f"{metrics['failed_routes']} ({metrics['failure_rate']:.2f}%)"],
            ['Average Hops (Success)', f"{metrics['avg_hops']:.2f}"],
            ['Total Queue Load', f"{metrics['total_queue_load']} tasks"]
        ]
        
        print(tabulate(metrics_table, headers=['Metric', 'Value'], tablefmt='grid'))
        print(f"{Fore.CYAN}{'='*70}\n")
        
        return metrics



if __name__ == "__main__":
    import sys
    import os
    
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from network.topologysetup import NetworkTopology
    
    print(f"{Fore.MAGENTA}{'='*70}")
    print(f"{Fore.MAGENTA}TESTING BACKPRESSURE ROUTING ALGORITHM")
    print(f"{Fore.MAGENTA}{'='*70}\n")
    
    print(f"{Fore.YELLOW}Step 1: Creating network topology...")
    network = NetworkTopology(
        num_iot_devices=5,
        num_edge_nodes=2,
        num_fog_nodes=3,
        num_cloud_nodes=1
    )
    
 
    network.create_topology()
    
    print(f"{Fore.YELLOW}✓ Topology created with:")
    print(f"   - IoT nodes: {len(network.iot_nodes)}")
    print(f"   - Edge nodes: {len(network.edge_nodes)}")
    print(f"   - Fog nodes: {len(network.fog_nodes)}")
    print(f"   - Cloud nodes: {len(network.cloud_nodes)}\n")
    
    print(f"{Fore.YELLOW}Step 2: Initializing Backpressure Router...")
    router = BackpressureRouter(network)
    
    print(f"{Fore.YELLOW}Step 3: Routing tasks...")
    results = router.route_batch_tasks(num_tasks=20)
    
    router.display_routing_table(results)
    
    metrics = router.get_performance_metrics()
    
    print(f"{Fore.GREEN}✓ Backpressure Routing Algorithm tested successfully!\n")