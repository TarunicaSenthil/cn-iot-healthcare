import networkx as nx
import matplotlib.pyplot as plt
import random
from colorama import Fore, Style, init


init(autoreset=True)


class NetworkTopology:
    def __init__(self, num_iot_devices=5, num_edge_nodes=2, num_fog_nodes=3, num_cloud_nodes=1):
        """
        Initialize network topology parameters
        
        Args:
            num_iot_devices: Number of IoT sensor devices (patients)
            num_edge_nodes: Number of edge gateway nodes
            num_fog_nodes: Number of fog computing nodes
            num_cloud_nodes: Number of cloud datacenter nodes
        """
        self.num_iot_devices = num_iot_devices
        self.num_edge_nodes = num_edge_nodes
        self.num_fog_nodes = num_fog_nodes
        self.num_cloud_nodes = num_cloud_nodes
        
        
        self.graph = nx.DiGraph()
        
       
        self.iot_nodes = []
        self.edge_nodes = []
        self.fog_nodes = []
        self.cloud_nodes = []
        
       
        self.link_bandwidths = {} 
        self.link_delays = {}      
        self.node_capacities = {}  
        self.node_queues = {}      
        
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Initializing Network Topology")
        print(f"{Fore.CYAN}{'='*60}")
        
    def create_topology(self):
        """
        Create the complete hierarchical network topology
        """
        print(f"\n{Fore.GREEN}[1/5] Creating IoT Device Layer...")
        self._create_iot_layer()
        
        print(f"{Fore.GREEN}[2/5] Creating Edge Gateway Layer...")
        self._create_edge_layer()
        
        print(f"{Fore.GREEN}[3/5] Creating Fog Computing Layer...")
        self._create_fog_layer()
        
        print(f"{Fore.GREEN}[4/5] Creating Cloud Datacenter Layer...")
        self._create_cloud_layer()
        
        print(f"{Fore.GREEN}[5/5] Establishing Network Links...")
        self._create_links()
        
        print(f"\n{Fore.YELLOW}Network Topology Created Successfully!")
        self._print_topology_summary()
        
        return self.graph
    
    def _create_iot_layer(self):
        """Create IoT sensor devices (bottom layer)"""
        for i in range(self.num_iot_devices):
            node_id = f"IoT_{i+1}"
            self.iot_nodes.append(node_id)
            
            
            self.graph.add_node(
                node_id,
                layer='iot',
                type='sensor',
                data_rate=random.uniform(0.5, 2.0),  # MB/s
                battery_level=random.uniform(70, 100),  # %
                priority=random.choice(['high', 'medium', 'low'])
            )
            
           
            self.node_queues[node_id] = 0
            
    def _create_edge_layer(self):
        """Create edge gateway nodes"""
        for i in range(self.num_edge_nodes):
            node_id = f"Edge_{i+1}"
            self.edge_nodes.append(node_id)
            
            
            self.graph.add_node(
                node_id,
                layer='edge',
                type='gateway',
                cpu_capacity=random.uniform(1000, 2000),  # MIPS
                memory=random.uniform(2, 4),  # GB
                latency_to_fog=random.uniform(10, 30)  # ms
            )
            
           
            self.node_capacities[node_id] = random.uniform(1000, 2000)
            self.node_queues[node_id] = 0
            
    def _create_fog_layer(self):
        """Create fog computing nodes"""
        for i in range(self.num_fog_nodes):
            node_id = f"Fog_{i+1}"
            self.fog_nodes.append(node_id)
            
            
            self.graph.add_node(
                node_id,
                layer='fog',
                type='compute',
                cpu_capacity=random.uniform(3000, 5000),  # MIPS
                memory=random.uniform(8, 16),  # GB
                latency_to_cloud=random.uniform(50, 100)  # ms
            )
            
           
            self.node_capacities[node_id] = random.uniform(3000, 5000)
            self.node_queues[node_id] = 0
            
    def _create_cloud_layer(self):
        """Create cloud datacenter nodes (top layer)"""
        for i in range(self.num_cloud_nodes):
            node_id = f"Cloud_{i+1}"
            self.cloud_nodes.append(node_id)
            
            
            self.graph.add_node(
                node_id,
                layer='cloud',
                type='datacenter',
                cpu_capacity=10000,  
                memory=64,  
                storage=1000  
            )
            
            
            self.node_capacities[node_id] = 10000
            self.node_queues[node_id] = 0
            
    def _create_links(self):
        """Create links between layers"""
        
        for iot in self.iot_nodes:
            
            edge = random.choice(self.edge_nodes)
            self.graph.add_edge(iot, edge)
            
            
            self.link_bandwidths[(iot, edge)] = random.uniform(5, 20)  # Mbps
            self.link_delays[(iot, edge)] = random.uniform(1, 5)  # ms
            
        
        for edge in self.edge_nodes:
            
            connected_fogs = random.sample(self.fog_nodes, 
                                          min(2, len(self.fog_nodes)))
            for fog in connected_fogs:
                self.graph.add_edge(edge, fog)
                
                self.link_bandwidths[(edge, fog)] = random.uniform(50, 100)  # Mbps
                self.link_delays[(edge, fog)] = random.uniform(10, 30)  # ms
                
        
        for fog in self.fog_nodes:
            
            for cloud in self.cloud_nodes:
                self.graph.add_edge(fog, cloud)
                
                self.link_bandwidths[(fog, cloud)] = random.uniform(100, 500)  # Mbps
                self.link_delays[(fog, cloud)] = random.uniform(50, 100)  # ms
                
    def _print_topology_summary(self):
        """Print network topology summary"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}NETWORK TOPOLOGY SUMMARY")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.WHITE}Total Nodes: {self.graph.number_of_nodes()}")
        print(f"{Fore.WHITE}Total Links: {self.graph.number_of_edges()}")
        print(f"\n{Fore.YELLOW}Layer Distribution:")
        print(f"  • IoT Devices:    {len(self.iot_nodes)}")
        print(f"  • Edge Gateways:  {len(self.edge_nodes)}")
        print(f"  • Fog Nodes:      {len(self.fog_nodes)}")
        print(f"  • Cloud Nodes:    {len(self.cloud_nodes)}")
        print(f"{Fore.CYAN}{'='*60}\n")
        
    def visualize_topology(self, save_path=None):
        """
        Visualize the network topology
        
        Args:
            save_path: Path to save the visualization (optional)
        """
        plt.figure(figsize=(14, 10))
        
       
        pos = {}
        
       
        for i, node in enumerate(self.iot_nodes):
            pos[node] = (i * 2, 0)
            
        
        for i, node in enumerate(self.edge_nodes):
            pos[node] = (i * 4 + 1, 2)
            
       
        for i, node in enumerate(self.fog_nodes):
            pos[node] = (i * 3 + 1, 4)
            
        
        for i, node in enumerate(self.cloud_nodes):
            pos[node] = (len(self.fog_nodes) * 1.5, 6)
            
        
        node_colors = []
        for node in self.graph.nodes():
            if node in self.iot_nodes:
                node_colors.append('#FF6B6B')  
            elif node in self.edge_nodes:
                node_colors.append('#4ECDC4')  
            elif node in self.fog_nodes:
                node_colors.append('#45B7D1') 
            else:
                node_colors.append('#FFA07A')  
                
       
        nx.draw_networkx_nodes(self.graph, pos, node_color=node_colors, 
                              node_size=800, alpha=0.9)
        nx.draw_networkx_labels(self.graph, pos, font_size=8, font_weight='bold')
        nx.draw_networkx_edges(self.graph, pos, edge_color='gray', 
                              arrows=True, arrowsize=15, width=1.5, alpha=0.6)
        
        
        plt.text(-1, 0, 'IoT Layer', fontsize=12, fontweight='bold', color='red')
        plt.text(-1, 2, 'Edge Layer', fontsize=12, fontweight='bold', color='cyan')
        plt.text(-1, 4, 'Fog Layer', fontsize=12, fontweight='bold', color='blue')
        plt.text(-1, 6, 'Cloud Layer', fontsize=12, fontweight='bold', color='orange')
        
        plt.title('Edge-Fog-Cloud Healthcare IoT Network Topology', 
                 fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"{Fore.GREEN}Topology visualization saved to: {save_path}")
        
        plt.show()
        
    def get_all_paths(self, source, destination):
        """
        Get all possible paths from source to destination
        
        Args:
            source: Source node ID
            destination: Destination node ID
            
        Returns:
            List of all paths
        """
        try:
            paths = list(nx.all_simple_paths(self.graph, source, destination))
            return paths
        except nx.NetworkXNoPath:
            return []



if __name__ == "__main__":
    import os
    
    print(f"{Fore.MAGENTA}{'='*60}")
    print(f"{Fore.MAGENTA}TESTING NETWORK TOPOLOGY MODULE")
    print(f"{Fore.MAGENTA}{'='*60}\n")
    
    
    network = NetworkTopology(
        num_iot_devices=5,
        num_edge_nodes=2,
        num_fog_nodes=3,
        num_cloud_nodes=1
    )
    
    
    graph = network.create_topology()
    
   
    print(f"\n{Fore.YELLOW}Testing Path Discovery:")
    source = network.iot_nodes[0]
    destination = network.cloud_nodes[0]
    paths = network.get_all_paths(source, destination)
    
    print(f"\nPaths from {source} to {destination}:")
    for i, path in enumerate(paths, 1):
        print(f"  Path {i}: {' → '.join(path)}")
    
    
    print(f"\n{Fore.CYAN}Generating visualization...")
    
    
    results_dir = os.path.join(os.getcwd(), 'results', 'graphs')
    os.makedirs(results_dir, exist_ok=True)
    
    save_path = os.path.join(results_dir, 'network_topology.png')
    network.visualize_topology(save_path=save_path)
    
    print(f"\n{Fore.GREEN}✓ Topology module tested successfully!")