from __future__ import annotations

from typing import Any, Callable


class DOMTree:
    """DOM Tree.

    Args:
        tree: Chrome's DOM tree dictionary.
    """
    def __init__(self, tree: Any) -> None:
        self.root: DOMNode = self._build_tree(tree['root'])

    def _build_tree(self, root: Any, level: int = 0) -> DOMNode:
        """Build DOM tree and return the root."""
        node = DOMNode(root)
        for child in root.get('children', []):
            child_node = self._build_tree(child, level + 1)
            node.append_child(child_node)

        return node

    def search(self, predicate: Callable[[DOMNode], bool]) -> list[DOMNode]:
        """Search nodes in the DOM Tree using `predicate`."""
        def _search(node, found_nodes=[]):
            if predicate(node):
                found_nodes.append(node)

            for child in node.children:
                _search(child, found_nodes)

            return found_nodes

        return _search(self.root)

    def __repr__(self) -> str:
        classname = self.__class__.__name__
        return f'{classname}(root={self.root!r})'


class DOMNode:
    """DOM Node.

    Args:
        node: Chrome's Node dictionary.
    """
    def __init__(self, node: Any) -> None:
        self.node_id: int = node['nodeId']
        self.backend_node_id: int = node['backendNodeId']
        self.node_type: int = node['nodeType']
        self.node_name: str = node['nodeName']
        self.local_name: str = node['localName']
        self.value: Any = node['nodeValue']
        self.children: list[DOMNode] = []
        self.attributes: dict[str, Any] = {}

        if 'attributes' in node:
            attributes_list = node['attributes']
            attributes_list_count = len(attributes_list)
            assert attributes_list_count % 2 == 0
            for name_idx in range(0, attributes_list_count, 2):
                self.attributes[attributes_list[name_idx]] = attributes_list[name_idx + 1]

    def append_child(self, node: DOMNode) -> None:
        self.children.append(node)

    def __repr__(self) -> str:
        classname = self.__class__.__name__
        return (f'{classname}(node_id={self.node_id}, name={self.local_name}, '
                f'attributes={self.attributes}, children={len(self.children)})')
