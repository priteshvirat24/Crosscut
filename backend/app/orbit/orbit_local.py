import time
import logging
from .orbit_client import OrbitClient
from .orbit_models import OrbitQueryPayload, OrbitResponse, OrbitNode, OrbitEdge

logger = logging.getLogger(__name__)

class OrbitLocalClient(OrbitClient):
    """
    Mocked Orbit Local Client for single-repo analysis.
    """
    def __init__(self, db_path: str = "~/.orbit/graph.duckdb"):
        self.db_path = db_path

    def get_mode_info(self) -> str:
        return "Orbit Local Active (Single Repository Scope)"

    def query(self, payload: OrbitQueryPayload) -> OrbitResponse:
        logger.info(f"Executing `orbit sql` for: {payload.query.node.entity}")
        time.sleep(0.5)

        # Local mode only finds tests in the current repo
        return OrbitResponse(
            nodes=[
                OrbitNode(id="local_test_1", entity="File", properties={"name": "test_local.py"})
            ],
            edges=[]
        )
