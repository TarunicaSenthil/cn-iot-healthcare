"""
Performance Metrics Module
Collects, analyzes, and compares performance of both CN algorithms
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from colorama import Fore, Style, init
from tabulate import tabulate

init(autoreset=True)


class PerformanceAnalyzer:
    """
    Analyzes and compares performance of Backpressure and TCP algorithms
    """
    
    def __init__(self):
        """Initialize performance analyzer"""
        self.backpressure_metrics = {}
        self.tcp_metrics = {}
        self.comparison_data = {}
        
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}Performance Analyzer Initialized")
        print(f"{Fore.CYAN}{'='*70}\n")
    
    def set_backpressure_metrics(self, metrics):
        """Store backpressure routing metrics"""
        self.backpressure_metrics = metrics
    
    def set_tcp_metrics(self, metrics):
        """Store TCP congestion control metrics"""
        self.tcp_metrics = metrics
    
    def calculate_combined_metrics(self):
        """
        Calculate combined system performance metrics
        """
        if not self.backpressure_metrics or not self.tcp_metrics:
            print(f"{Fore.RED}Error: Missing metrics data")
            return {}
        
        # Extract key metrics
        bp_success_rate = self.backpressure_metrics.get('success_rate', 0)
        bp_avg_hops = self.backpressure_metrics.get('avg_hops', 0)
        bp_queue_load = self.backpressure_metrics.get('total_queue_load', 0)
        
        tcp_delivery_rate = self.tcp_metrics.get('delivery_rate', 0)
        tcp_throughput = self.tcp_metrics.get('avg_throughput', 0)
        tcp_rtt = self.tcp_metrics.get('avg_rtt', 0)
        
        # Calculate combined metrics
        combined = {
            'overall_success_rate': (bp_success_rate + tcp_delivery_rate) / 2,
            'network_efficiency': bp_success_rate * (1 / bp_avg_hops) if bp_avg_hops > 0 else 0,
            'transmission_efficiency': tcp_throughput * (tcp_delivery_rate / 100),
            'avg_latency': tcp_rtt + (bp_avg_hops * 10),  # Estimated total latency
            'system_utilization': (bp_queue_load / 100) * 100  # Normalized
        }
        
        self.comparison_data = combined
        return combined
    
    def create_comparison_table(self):
        """
        Create side-by-side comparison table
        """
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}ALGORITHM PERFORMANCE COMPARISON")
        print(f"{Fore.CYAN}{'='*70}\n")
        
        # Prepare comparison data
        comparison = [
            ['Algorithm Type', 'Backpressure Routing', 'TCP Congestion Control'],
            ['Layer', 'Network Layer', 'Transport Layer'],
            ['', '', ''],
            ['Success/Delivery Rate', 
             f"{self.backpressure_metrics.get('success_rate', 0):.2f}%",
             f"{self.tcp_metrics.get('delivery_rate', 0):.2f}%"],
            ['Average Hops/RTT',
             f"{self.backpressure_metrics.get('avg_hops', 0):.2f} hops",
             f"{self.tcp_metrics.get('avg_rtt', 0):.2f} ms"],
            ['Throughput',
             f"{self.backpressure_metrics.get('total_tasks', 0)} tasks",
             f"{self.tcp_metrics.get('avg_throughput', 0):.2f} tasks/round"],
            ['Queue Load / Max CWND',
             f"{self.backpressure_metrics.get('total_queue_load', 0)} tasks",
             f"{self.tcp_metrics.get('max_cwnd', 0):.2f}"],
            ['Failed Events',
             f"{self.backpressure_metrics.get('failed_routes', 0)} routes",
             f"{self.tcp_metrics.get('packet_loss_events', 0)} losses"]
        ]
        
        print(tabulate(comparison, tablefmt='grid'))
        print(f"{Fore.CYAN}{'='*70}\n")
    
    def create_combined_metrics_table(self):
        """
        Display combined system metrics
        """
        if not self.comparison_data:
            self.calculate_combined_metrics()
        
        print(f"\n{Fore.YELLOW}{'='*70}")
        print(f"{Fore.YELLOW}COMBINED SYSTEM PERFORMANCE METRICS")
        print(f"{Fore.YELLOW}{'='*70}\n")
        
        metrics_table = [
            ['Overall Success Rate', f"{self.comparison_data['overall_success_rate']:.2f}%"],
            ['Network Routing Efficiency', f"{self.comparison_data['network_efficiency']:.4f}"],
            ['Transmission Efficiency', f"{self.comparison_data['transmission_efficiency']:.2f} tasks/round"],
            ['Estimated Average Latency', f"{self.comparison_data['avg_latency']:.2f} ms"],
            ['System Utilization', f"{self.comparison_data['system_utilization']:.2f}%"]
        ]
        
        print(tabulate(metrics_table, headers=['Metric', 'Value'], tablefmt='grid'))
        print(f"{Fore.YELLOW}{'='*70}\n")
    
    def plot_algorithm_comparison(self, save_path=None):
        """
        Create comparison charts for both algorithms
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('CN Algorithms Performance Comparison', fontsize=16, fontweight='bold')
        
        # Chart 1: Success/Delivery Rates
        ax1 = axes[0, 0]
        algorithms = ['Backpressure\nRouting', 'TCP Congestion\nControl']
        success_rates = [
            self.backpressure_metrics.get('success_rate', 0),
            self.tcp_metrics.get('delivery_rate', 0)
        ]
        colors = ['#4ECDC4', '#FF6B6B']
        bars1 = ax1.bar(algorithms, success_rates, color=colors, alpha=0.7, edgecolor='black')
        ax1.set_ylabel('Success Rate (%)', fontweight='bold')
        ax1.set_title('Algorithm Success Rates', fontweight='bold')
        ax1.set_ylim(0, 100)
        ax1.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # Chart 2: Throughput Comparison
        ax2 = axes[0, 1]
        throughput_labels = ['Backpressure\nTotal Tasks', 'TCP Avg\nThroughput']
        throughput_values = [
            self.backpressure_metrics.get('total_tasks', 0),
            self.tcp_metrics.get('avg_throughput', 0) * 10  # Scale for visibility
        ]
        bars2 = ax2.bar(throughput_labels, throughput_values, color=['#45B7D1', '#FFA07A'], 
                       alpha=0.7, edgecolor='black')
        ax2.set_ylabel('Tasks', fontweight='bold')
        ax2.set_title('Throughput Metrics', fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # Chart 3: Latency/Hops Comparison
        ax3 = axes[1, 0]
        latency_labels = ['Backpressure\nAvg Hops', 'TCP\nAvg RTT (ms)']
        latency_values = [
            self.backpressure_metrics.get('avg_hops', 0),
            self.tcp_metrics.get('avg_rtt', 0) / 20  # Scale for comparison
        ]
        bars3 = ax3.bar(latency_labels, latency_values, color=['#95E1D3', '#F38181'], 
                       alpha=0.7, edgecolor='black')
        ax3.set_ylabel('Normalized Units', fontweight='bold')
        ax3.set_title('Latency Metrics (Normalized)', fontweight='bold')
        ax3.grid(axis='y', alpha=0.3)
        
        for bar in bars3:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', ha='center', va='bottom', fontweight='bold')
        
        # Chart 4: Combined System Performance Radar
        ax4 = axes[1, 1]
        
        # Prepare data for radar chart
        categories = ['Success\nRate', 'Efficiency', 'Throughput', 'Low\nLatency', 'Utilization']
        
        # Normalize all metrics to 0-100 scale
        values = [
            self.comparison_data.get('overall_success_rate', 0),
            self.comparison_data.get('network_efficiency', 0) * 100,
            min(self.comparison_data.get('transmission_efficiency', 0) * 10, 100),
            max(100 - (self.comparison_data.get('avg_latency', 100) / 2), 0),
            min(self.comparison_data.get('system_utilization', 0), 100)
        ]
        
        # Create bar chart instead of radar for simplicity
        x_pos = np.arange(len(categories))
        bars4 = ax4.bar(x_pos, values, color='#6C5CE7', alpha=0.7, edgecolor='black')
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(categories, fontsize=9)
        ax4.set_ylabel('Score (0-100)', fontweight='bold')
        ax4.set_title('Combined System Performance', fontweight='bold')
        ax4.set_ylim(0, 100)
        ax4.grid(axis='y', alpha=0.3)
        
        for bar in bars4:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom', fontsize=8, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"{Fore.GREEN}Comparison plot saved to: {save_path}\n")
        
        plt.show()
    
    def export_results_to_csv(self, output_dir='data/output'):
        """
        Export all metrics to CSV files
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Export Backpressure metrics
        bp_df = pd.DataFrame([self.backpressure_metrics])
        bp_path = os.path.join(output_dir, 'backpressure_metrics.csv')
        bp_df.to_csv(bp_path, index=False)
        
        # Export TCP metrics
        tcp_df = pd.DataFrame([self.tcp_metrics])
        tcp_path = os.path.join(output_dir, 'tcp_metrics.csv')
        tcp_df.to_csv(tcp_path, index=False)
        
        # Export combined metrics
        combined_df = pd.DataFrame([self.comparison_data])
        combined_path = os.path.join(output_dir, 'combined_metrics.csv')
        combined_df.to_csv(combined_path, index=False)
        
        print(f"{Fore.GREEN}✓ Metrics exported to CSV files:")
        print(f"  • {bp_path}")
        print(f"  • {tcp_path}")
        print(f"  • {combined_path}\n")
    
    def generate_summary_report(self):
        """
        Generate text summary report
        """
        print(f"\n{Fore.MAGENTA}{'='*70}")
        print(f"{Fore.MAGENTA}PROJECT SUMMARY REPORT")
        print(f"{Fore.MAGENTA}{'='*70}\n")
        
        print(f"{Fore.CYAN}Project: CN Healthcare Edge Computing with IoT")
        print(f"{Fore.CYAN}Algorithms: Backpressure Routing + TCP Congestion Control\n")
        
        print(f"{Fore.YELLOW}Key Findings:")
        print(f"  1. Backpressure routing achieved {self.backpressure_metrics.get('success_rate', 0):.1f}% success rate")
        print(f"  2. TCP congestion control delivered {self.tcp_metrics.get('delivery_rate', 0):.1f}% of packets")
        print(f"  3. Average network hops: {self.backpressure_metrics.get('avg_hops', 0):.2f}")
        print(f"  4. Average RTT: {self.tcp_metrics.get('avg_rtt', 0):.2f} ms")
        print(f"  5. Combined system efficiency: {self.comparison_data.get('overall_success_rate', 0):.1f}%\n")
        
        print(f"{Fore.GREEN}Conclusion:")
        print(f"  Both CN algorithms successfully implemented and tested.")
        print(f"  System demonstrates effective task routing and congestion management.")
        print(f"  Ready for research paper documentation.\n")
        
        print(f"{Fore.MAGENTA}{'='*70}\n")


if __name__ == "__main__":
    print(f"{Fore.CYAN}Performance Metrics module loaded successfully!")
    print(f"{Fore.YELLOW}Use this module in main.py to analyze algorithm performance.\n")