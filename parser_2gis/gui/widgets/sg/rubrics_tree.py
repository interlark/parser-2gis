from __future__ import annotations

from typing import Any

import PySimpleGUI as sg


class RubricsTree(sg.Tree):  # type: ignore
    """Rubrics tree.

    Args:
        rubrics: Rubrics dictionary.
        image_parent: Image for parent rubric.
        image_item: Image for rubric.
    """
    def __init__(self, rubrics: dict[str, Any], image_parent: bytes | None = None,
                 image_item: bytes | None = None, *args, **kwargs) -> None:
        self._rubrics = rubrics
        self._image_parent = image_parent
        self._image_item = image_item
        self.ShowExpanded = False
        super().__init__(*args, **kwargs, data=self._build_tree())

    def _build_tree(self, root_code: str = '0',
                    tree: sg.TreeData | None = None) -> sg.TreeData:
        """Get tree data out of `_rubrics`.

        Args:
            root_code: Root key (always '0').
            tree: Tree data (always None).

        Returns:
            Generated tree data.
        """
        node = self._rubrics[root_code]
        parent_code = node['parentCode']
        is_leaf = not bool(node['children'])

        visible = node.get('visible', True)
        if not visible:
            return

        if root_code == '0':
            tree = sg.TreeData()

        if root_code != '0':
            # Change root to sg's '', instead of default '0'
            assert tree
            tree.Insert('' if parent_code == '0' else parent_code,
                        root_code, node['label'], values=[],
                        icon=self._image_item if is_leaf else self._image_parent)

        for child_code in node['children']:
            self._build_tree(child_code, tree)

        return tree

    def expand(self, expand: bool = True) -> None:
        """Expand tree.

        Args:
            expand: Whether to expand or collapse the tree.
        """
        def recursive_expand(parent: str = '') -> None:
            self.widget.item(parent, open=expand)
            for child in self.widget.get_children(parent):
                recursive_expand(child)

        recursive_expand()

    def clear(self) -> None:
        """Clear tree."""
        self.widget.delete(*self.widget.get_children())

    def filter(self, query: str) -> None:
        """Filter tree by user search query.

        Args:
            query: User search query.
        """
        def mark_visible_nodes(root_code: str = '0') -> bool:
            """Tree traversal with marking nodes
            matches specified user query.

            Args:
                root_code: Root key (always '0').

            Returns:
                Root node visibility.
            """
            node = self._rubrics[root_code]
            children = node['children']
            label = node['label'] or ''

            visible = False
            for child in children:
                if mark_visible_nodes(child):
                    visible = True

            if not visible:
                visible = query in label.lower()

            node['visible'] = visible
            return visible

        self.ShowExpanded = True
        query = query.lower()
        if mark_visible_nodes():
            self.update(values=self._build_tree())
        else:
            self.clear()
