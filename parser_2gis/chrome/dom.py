from __future__ import annotations

from typing import Callable, Dict, List

from pydantic import BaseModel, Field, validator


class DOMNode(BaseModel):
    """DOM Node.

    Attributes:
        id: Node identifier.
        backend_id: The BackendNodeId for this node.
        type: Node's type.
        name: Node's name.
        local_name: Node's local name.
        value: Node's value.
        children: Node's children.
        attributes: Node's attributes.
    """
    id: int = Field(..., alias='nodeId')
    backend_id: int = Field(..., alias='backendNodeId')
    type: int = Field(..., alias='nodeType')
    name: str = Field(..., alias='nodeName')
    local_name: str = Field(..., alias='localName')
    value: str = Field(..., alias='nodeValue')
    children: List[DOMNode] = []
    attributes: Dict[str, str] = {}

    @validator('attributes', pre=True)
    def validate_attributes(cls, attributes_list: list[str]) -> dict[str, str]:
        attributes = {}
        attributes_list_count = len(attributes_list)
        assert attributes_list_count % 2 == 0
        for name_idx in range(0, attributes_list_count, 2):
            attributes[attributes_list[name_idx]] = attributes_list[name_idx + 1]

        return attributes

    def search(self, predicate: Callable[[DOMNode], bool]) -> list[DOMNode]:
        """Search nodes in the DOM Tree using `predicate`."""
        def _search(node: DOMNode, found_nodes: list[DOMNode]) -> None:
            if predicate(node):
                found_nodes.append(node)

            for child in node.children:
                _search(child, found_nodes)

        found_nodes: list[DOMNode] = []
        _search(self, found_nodes)
        return found_nodes
