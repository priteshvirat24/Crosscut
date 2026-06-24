from .orbit_client import OrbitClient
from .orbit_queries import (
    build_symbol_lookup_query,
    build_incoming_call_query,
    build_cross_repo_traversal_query,
    build_test_discovery_query,
)

class OrbitDiscoveryService:
    """
    High-level orchestrator that uses the Orbit Client to discover tests impacted by a changed symbol.
    """
    def __init__(self, client: OrbitClient):
        self.client = client

    def get_mode(self) -> str:
        return self.client.get_mode_info()

    def discover_impacted_tests(self, symbol_name: str):
        steps = []

        # Step 1: Symbol Lookup
        q1 = build_symbol_lookup_query(symbol_name)
        res1 = self.client.query(q1)
        steps.append({"phase": "Symbol Lookup", "query": q1.model_dump(), "nodes_found": len(res1.nodes)})

        # Step 2: Incoming Call Traversal
        if not res1.nodes:
            return {"steps": steps, "final_tests": []}
            
        symbol_id = res1.nodes[0].id
        q2 = build_incoming_call_query(symbol_id)
        res2 = self.client.query(q2)
        steps.append({"phase": "Dependency Traversal", "query": q2.model_dump(), "nodes_found": len(res2.nodes)})

        # Step 3: Cross Repo Discovery
        q3 = build_cross_repo_traversal_query(symbol_id)
        res3 = self.client.query(q3)
        repos = [n for n in res3.nodes if n.entity == "Repository"]
        steps.append({"phase": "Cross Repository Discovery", "query": q3.model_dump(), "nodes_found": len(repos)})

        # Step 4: Test Selection
        repo_ids = [r.id for r in repos]
        q4 = build_test_discovery_query(repo_ids)
        res4 = self.client.query(q4)
        tests = [n for n in res4.nodes if n.entity == "File"]
        steps.append({"phase": "Test Selection", "query": q4.model_dump(), "nodes_found": len(tests)})

        return {
            "mode": self.get_mode(),
            "steps": steps,
            "final_tests": [t.model_dump() for t in tests]
        }
