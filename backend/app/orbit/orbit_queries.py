from .orbit_models import OrbitQuery, OrbitQueryNode, OrbitFilter, OrbitQueryPayload

def build_symbol_lookup_query(symbol_name: str) -> OrbitQueryPayload:
    """Finds a specific symbol (function, class) in the graph."""
    return OrbitQueryPayload(
        query=OrbitQuery(
            query_type="traversal",
            node=OrbitQueryNode(
                id="symbol_lookup",
                entity="Function",
                filters={
                    "name": OrbitFilter(op="equals", value=symbol_name)
                }
            ),
            limit=1
        )
    )

def build_incoming_call_query(symbol_id: str, max_depth: int = 5) -> OrbitQueryPayload:
    """Traverses incoming calls up to max_depth."""
    return OrbitQueryPayload(
        query=OrbitQuery(
            query_type="traversal",
            node=OrbitQueryNode(
                id=symbol_id,
                entity="Function",
            ),
            limit=1000
        )
    )

def build_cross_repo_traversal_query(root_node_id: str) -> OrbitQueryPayload:
    """Discovers cross-repository dependencies and services calling a node."""
    return OrbitQueryPayload(
        query=OrbitQuery(
            query_type="path",
            node=OrbitQueryNode(
                id=root_node_id,
                entity="Repository",
            ),
            limit=500
        )
    )

def build_test_discovery_query(service_ids: list[str]) -> OrbitQueryPayload:
    """Finds test files mapped to the discovered services."""
    return OrbitQueryPayload(
        query=OrbitQuery(
            query_type="neighbor",
            node=OrbitQueryNode(
                id="test_discovery",
                entity="File",
                filters={
                    "file_type": OrbitFilter(op="equals", value="test")
                }
            ),
            limit=1000
        )
    )
