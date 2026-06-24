from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class OrbitNode(BaseModel):
    id: str
    entity: str
    properties: Dict[str, Any] = Field(default_factory=dict)

class OrbitEdge(BaseModel):
    id: str
    source_id: str
    target_id: str
    relationship: str
    properties: Dict[str, Any] = Field(default_factory=dict)

class OrbitFilter(BaseModel):
    op: str
    value: Any

class OrbitQueryNode(BaseModel):
    id: str
    entity: str
    filters: Optional[Dict[str, OrbitFilter]] = None

class OrbitQuery(BaseModel):
    query_type: str
    node: OrbitQueryNode
    limit: int = 100

class OrbitQueryPayload(BaseModel):
    query: OrbitQuery

class OrbitResponse(BaseModel):
    nodes: List[OrbitNode]
    edges: List[OrbitEdge]
