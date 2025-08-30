from tree_sitter import Node as TreeNode


def tree_to_sexp(node: TreeNode) -> str:
    children = [tree_to_sexp(child) for child in node.children]
    return f"({node.type} {' '.join(children)})" if children else node.type