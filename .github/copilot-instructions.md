## Quick context

This repository is a simulation project modeling an Edge–Fog–Cloud IoT network and routing experiments. Key code lives under `src/`:

- `src/network/topologysetup.py` — Network topology builder (NetworkTopology class).
- `src/algorithms/backpressure_routing.py` — Backpressure routing algorithm and runner.
- `src/algorithms/tcp_congestion.py` — (placeholder/empty) TCP congestion experiments.
- `src/utils/performancemetrics.py` — (empty) intended for metrics collection.

Dependencies discovered in `requirements.txt`: networkx, matplotlib, colorama, tabulate, numpy, pandas, seaborn, scipy.

## Big-picture architecture

- The system builds a directed graph (NetworkX) with hierarchical layers: IoT -> Edge -> Fog -> Cloud.
- Algorithms consume the topology (pass a NetworkTopology instance) and use the graph, node queues and link metadata.
- Data flow: tasks originate at IoT nodes, traverse Edge/Fog up to Cloud; routing decisions update `node_queues` and are recorded by algorithm classes.

## Important repo-specific conventions & gotchas (read before editing or running)

- Several files contain non-standard typos that break normal Python imports and runtime behavior. Search for these exact tokens and fix them before running tests:
  - `_init_` should be `__init__` (many package init files are named `src/*/_init_.py`).
  - `_name_ == "_main_"` should be `__name__ == "__main__"` in script blocks.
  - Constructors are implemented as `def _init_(self, ...)` — replace with `def __init__(self, ...)` in classes (example: `NetworkTopology` in `src/network/topologysetup.py` and `BackpressureRouter` in `src/algorithms/backpressure_routing.py`).
  - Module filenames vs imports: code imports `network.topology_setup` or `topology_setup` in some places, but the file is `topologysetup.py`. Keep file/module names consistent (use underscores in both filename and imports) or adapt imports.

## Concrete examples from codebase (things to fix or follow)

- In `src/network/topologysetup.py` the class is `NetworkTopology` but its constructor uses `_init_`. Fix to `__init__` and ensure `__name__` guard is `if __name__ == '__main__':`.
- In `src/algorithms/backpressure_routing.py` the bottom-of-file runner imports `from network.topology_setup import NetworkTopology` but the real file is `topologysetup.py`. Either rename file to `topology_setup.py` or update the import to `from network.topologysetup import NetworkTopology`.

## How to run / reproduce (discoverable commands)

1) Install dependencies (Windows PowerShell):

```powershell
python -m pip install -r requirements.txt
```

2) Quick smoke test (after fixing `_init_` and `__name__` issues): run the topology visualizer script:

```powershell
python src\network\topologysetup.py
```

If you prefer to run modules as packages, fix `__init__` names and run like:

```powershell
python -m src.network.topologysetup
```

## What an AI agent should do first (minimal, high-value edits)

1. Search-and-fix typos: run a repo-wide search for `_init_`, `_name_`, `_file_`, `topology_setup` and correct to the Python idioms (`__init__`, `__name__`, `__file__`). Commit small PRs with each logical change.
2. Normalize module filenames vs imports. Prefer snake_case filenames (`topology_setup.py`) and update imports accordingly.
3. Add a small test harness (or unit test) that imports `NetworkTopology`, instantiates it, calls `create_topology()` and asserts at least one node and one edge exist.

## Integration points / external dependencies

- Visualization uses `matplotlib` and saves to `results/graphs` — the project expects that directory to exist (scripts attempt to create it).
- Algorithm modules read/write to `NetworkTopology` attributes: `graph`, `node_queues`, `link_bandwidths`, `node_capacities`.

## Short checklist for PRs from an AI agent

- Run repository-wide static checks (search for the 3 common typo patterns above) and include a patch that fixes them.
- Run the topology script locally to ensure visualization works and that there are no import errors.
- Prefer small, targeted commits (fix constructor, fix __name__ guard, then fix imports).

---

If anything above is unclear or you'd like me to auto-apply the low-risk fixes (search-and-replace `_init_` -> `__init__`, fix `__name__` guards, and align one import), tell me which fixes to apply and I'll create a PR-ready patch and run a smoke test.
