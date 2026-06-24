import time
import logging
from .orbit_client import OrbitClient
from .orbit_models import OrbitQueryPayload, OrbitResponse, OrbitNode, OrbitEdge

logger = logging.getLogger(__name__)

class OrbitRemoteClient(OrbitClient):
    """
    Mocked Orbit Remote Client for the Transcend Hackathon Demo.
    Generates real Query DSL syntax but returns mocked JSON for the 'validate_payment()' scenario.
    """
    def __init__(self, group_path: str = "gitlab-org"):
        self.group_path = group_path

    def get_mode_info(self) -> str:
        return "Orbit Remote Active (Cross-Repository Analysis Enabled)"

    def query(self, payload: OrbitQueryPayload) -> OrbitResponse:
        logger.info(f"Executing `glab orbit remote query` for: {payload.query.node.entity}")
        
        # Simulate network latency
        time.sleep(1.5)

        # Mocking the demo scenario: validate_payment() -> 5 repos -> 12 tests
        nodes = []
        edges = []

        if payload.query.node.entity == "Function":
            nodes.append(OrbitNode(id="fn_validate_payment", entity="Function", properties={"name": "validate_payment", "repo": "payment-library"}))
            nodes.append(OrbitNode(id="fn_checkout", entity="Function", properties={"name": "checkout", "repo": "checkout-service"}))
            nodes.append(OrbitNode(id="fn_refund", entity="Function", properties={"name": "process_refund", "repo": "refund-service"}))
            
            edges.append(OrbitEdge(id="e1", source_id="fn_checkout", target_id="fn_validate_payment", relationship="CALLS"))
            edges.append(OrbitEdge(id="e2", source_id="fn_refund", target_id="fn_validate_payment", relationship="CALLS"))

        elif payload.query.node.entity == "Repository":
            repos = ["checkout-service", "analytics-service", "refund-service", "billing-service", "customer-service"]
            for r in repos:
                nodes.append(OrbitNode(id=f"repo_{r}", entity="Repository", properties={"name": r}))
                edges.append(OrbitEdge(id=f"e_repo_{r}", source_id=f"repo_{r}", target_id="repo_payment_library", relationship="DEPENDS_ON"))

        elif payload.query.node.entity == "File" and payload.query.node.filters and "file_type" in payload.query.node.filters:
            # Test discovery
            for i in range(12):
                nodes.append(OrbitNode(id=f"test_{i}", entity="File", properties={"file_type": "test", "name": f"test_suite_{i}.py"}))
                edges.append(OrbitEdge(id=f"e_test_{i}", source_id=f"test_{i}", target_id="fn_checkout", relationship="TESTS"))

        return OrbitResponse(nodes=nodes, edges=edges)
