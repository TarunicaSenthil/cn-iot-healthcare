import os
import sys
from colorama import Fore, Style, init

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from network.topologysetup import NetworkTopology
from algorithms.backpressure_routing import BackpressureRouter
from algorithms.tcp_congestion import TCPCongestionControl
from utils.performancemetrics import PerformanceAnalyzer

init(autoreset=True)


def print_header():
    print(f"\n{Fore.MAGENTA}{'='*80}")
    print(f"{Fore.MAGENTA}{'='*80}")
    print(f"{Fore.CYAN}    CN HEALTHCARE EDGE COMPUTING PROJECT")
    print(f"{Fore.CYAN}    Computer Networks Algorithms Implementation")
    print(f"{Fore.MAGENTA}{'='*80}")
    print(f"{Fore.MAGENTA}{'='*80}\n")

    print(f"{Fore.YELLOW}Project Title:")
    print(f"{Fore.WHITE}  Congestion-Aware Task Routing and Offloading for")
    print(f"{Fore.WHITE}  IoT Healthcare Networks\n")

    print(f"{Fore.YELLOW}CN Algorithms Implemented:")
    print(f"{Fore.GREEN}  ✓ Algorithm 1: Backpressure Routing (Network Layer)")
    print(f"{Fore.GREEN}  ✓ Algorithm 2: TCP Congestion Control (Transport Layer)\n")

    print(f"{Fore.YELLOW}Application Domain:")
    print(f"{Fore.WHITE}  Real-time Healthcare IoT with Edge-Fog-Cloud Architecture\n")

    print(f"{Fore.MAGENTA}{'='*80}\n")


def main():
    print_header()

    print(f"{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}STEP 1: NETWORK TOPOLOGY SETUP")
    print(f"{Fore.CYAN}{'='*80}\n")

    network = NetworkTopology(
        num_iot_devices=5,
        num_edge_nodes=2,
        num_fog_nodes=3,
        num_cloud_nodes=1
    )

    graph = network.create_topology()

    print(f"\n{Fore.YELLOW}Generating network topology visualization...")
    results_dir = os.path.join(os.getcwd(), 'results', 'graphs')
    os.makedirs(results_dir, exist_ok=True)

    topology_path = os.path.join(results_dir, 'network_topology.png')
    network.visualize_topology(save_path=topology_path)

    input(f"\n{Fore.YELLOW}Press Enter to continue to Algorithm 1...")

    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}STEP 2: BACKPRESSURE ROUTING ALGORITHM (Network Layer)")
    print(f"{Fore.CYAN}{'='*80}\n")

    router = BackpressureRouter(network)

    print(f"{Fore.YELLOW}Routing 20 healthcare monitoring tasks...\n")
    bp_results = router.route_batch_tasks(num_tasks=20)

    router.display_routing_table(bp_results)
    bp_metrics = router.get_performance_metrics()

    input(f"\n{Fore.YELLOW}Press Enter to continue to Algorithm 2...")

    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}STEP 3: TCP CONGESTION CONTROL ALGORITHM (Transport Layer)")
    print(f"{Fore.CYAN}{'='*80}\n")

    tcp = TCPCongestionControl(network, initial_cwnd=1, ssthresh=16)

    print(f"{Fore.YELLOW}Running TCP task transmission simulation...\n")
    tcp.send_tasks_batch(num_rounds=30)

    tcp_metrics = tcp.get_performance_metrics()

    print(f"\n{Fore.YELLOW}Generating TCP performance plots...")
    tcp_plot_path = os.path.join(results_dir, 'tcp_congestion_control.png')
    tcp.plot_congestion_window(save_path=tcp_plot_path)

    input(f"\n{Fore.YELLOW}Press Enter to see performance comparison...")

    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}STEP 4: PERFORMANCE ANALYSIS & ALGORITHM COMPARISON")
    print(f"{Fore.CYAN}{'='*80}\n")

    analyzer = PerformanceAnalyzer()
    analyzer.set_backpressure_metrics(bp_metrics)
    analyzer.set_tcp_metrics(tcp_metrics)

    combined_metrics = analyzer.calculate_combined_metrics()

    analyzer.create_comparison_table()
    analyzer.create_combined_metrics_table()

    print(f"{Fore.YELLOW}Generating algorithm comparison charts...")
    comparison_path = os.path.join(results_dir, 'algorithm_comparison.png')
    analyzer.plot_algorithm_comparison(save_path=comparison_path)

    print(f"\n{Fore.YELLOW}Exporting results to CSV files...")
    analyzer.export_results_to_csv(output_dir='data/output')

    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}STEP 5: FINAL SUMMARY REPORT")
    print(f"{Fore.CYAN}{'='*80}\n")

    analyzer.generate_summary_report()

    print(f"{Fore.GREEN}{'='*80}")
    print(f"{Fore.GREEN}✓ PROJECT EXECUTION COMPLETED SUCCESSFULLY!")
    print(f"{Fore.GREEN}{'='*80}\n")

    print(f"{Fore.YELLOW}Generated Files:")
    print(f"{Fore.WHITE}  📊 Network Topology:    results/graphs/network_topology.png")
    print(f"{Fore.WHITE}  📊 TCP Performance:     results/graphs/tcp_congestion_control.png")
    print(f"{Fore.WHITE}  📊 Algorithm Comparison: results/graphs/algorithm_comparison.png")
    print(f"{Fore.WHITE}  📄 Backpressure CSV:    data/output/backpressure_metrics.csv")
    print(f"{Fore.WHITE}  📄 TCP CSV:             data/output/tcp_metrics.csv")
    print(f"{Fore.WHITE}  📄 Combined CSV:        data/output/combined_metrics.csv\n")

    print(f"{Fore.CYAN}Next Steps:")
    print(f"{Fore.WHITE}  1. Review all generated graphs and CSV files")
    print(f"{Fore.WHITE}  2. Use metrics for research paper/presentation")
    print(f"{Fore.WHITE}  3. Modify parameters in main() for different scenarios")
    print(f"{Fore.WHITE}  4. Run again with: python src/main.py\n")

    print(f"{Fore.MAGENTA}{'='*80}\n")
    print(f"{Fore.GREEN}Thank you for using CN Healthcare Edge Computing System!")
    print(f"{Fore.MAGENTA}{'='*80}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}Execution interrupted by user.")
        print(f"{Fore.YELLOW}Exiting...\n")
    except Exception as e:
        print(f"\n{Fore.RED}Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()