from typing import Dict, List, Tuple
from functools import reduce
from tree_sitter import Node as TreeNode
from ast import Module, parse as ast_parse
from _modulecode_nodevisitor import ModuleCodeVisitor


def parse_codeonly_response(resp: str) -> str:
    resp_lines: List[str] = resp.split("\n")
    code_only: str = reduce(lambda acc, line: acc + "\n" + line, resp_lines[1:(len(resp_lines) - 1)], "").lstrip("\n")
    return code_only


def extract_focalmodule_code(codefile_path: str) -> Tuple[str, Dict[str, List[str]]]:
    """
        TODO: Finish description

        Returns
        -------
        Tuple[str, Dict[str, str]]
            Una tupla contenente:

                - L' intero codice estratto dal modulo
                - Un dizionario di liste di stringhe, indicizzato su stringhe, contenente:

                    - "imports": Una lista di stringhe contenente tutti gli imports completi del modulo.
                    - "froms": Una lista di stringhe contenente tutti gli imports parziali del modulo.
                    - "funcs": Una lista di stringhe contenente tutti le funzioni (del modulo) estratte.
                    - "classes": Una lista di stringhe contenente tutti le definizioni di classe estratte.
    """
    code_mod: Module
    code_mod_str: str
    with open(codefile_path, "r") as ftest:
        code_mod_str = reduce(lambda acc, x: acc + x, ftest.readlines(), "")

    result: Dict[str, List[str]] = extract_module_code(code_mod_str)

    return (code_mod_str, result)


def extract_module_code(module_code: str) -> Dict[str, List[str]]:
    """
        TODO: Finish Description

        Parameters
        ----------
        module_code

        Returns
        -------
        Dict[str, List[str]]
            - Un dizionario di liste di stringhe, indicizzato su stringhe, contenente:

                - "imports": Una lista di stringhe contenente tutti gli imports completi del modulo.
                - "froms": Una lista di stringhe contenente tutti gli imports parziali del modulo.
                - "funcs": Una lista di stringhe contenente tutti le funzioni (del modulo) estratte.
                - "classes": Una lista di stringhe contenente tutti le definizioni di classe estratte.
    """
    result: Dict[str, List[str]] = dict()

    module: Module = ast_parse(module_code)

    focal_visitor: ModuleCodeVisitor = ModuleCodeVisitor()
    focal_visitor.visit(module)
    mod_classes: List[str] = focal_visitor.classes_definitions()
    mod_funcs: List[str] = focal_visitor.funcs_definitions()
    mod_imports: List[str] = focal_visitor.imports()
    mod_froms: List[str] = focal_visitor.fromimports()

    result["imports"] = mod_imports
    result["froms"] = mod_froms
    result["funcs"] = mod_funcs
    result["classes"] = mod_classes

    return result


def extract_fbyf_funcprompt_code(module_node: TreeNode) -> Tuple[Tuple[List[TreeNode], List[TreeNode]], List[TreeNode]]:
    """

        Parameters
        ----------
            module_node: TreeNode
                Un nodo rappresentante l'intero modulo di codice da scomporre (corrispondente alla radice del CST)

        Returns
        -------
            Tuple[Tuple[List[TreeNode], List[TreeNode]], List[TreeNode]]
                Una Tupla di 2 oggetti contenente:

                    - [0]: Una tupla di Liste di TreeNode:
                        - [0]: La lista dei TreeNode "imports" trovati nel codice
                        - [1]: La lista dei TreeNode "from imports" trovati nel codice
                    - [1]: La lista di TreeNode di definizioni di funzioni trovate nel codice
    """
    ls_imports: List[TreeNode] = []
    ls_fromimps: List[TreeNode] = []
    ls_funcs: List[TreeNode] = []

    for child_node in module_node.children:
        if child_node.type == "import_statement":
            ls_imports.append(child_node)
        elif child_node.type == "import_from_statement":
            ls_fromimps.append(child_node)
        elif child_node.type == "block":
            for prob_func in child_node.children:
                if prob_func.type == "function_definition":
                    ls_funcs.append(prob_func)

    return ((ls_imports, ls_fromimps), ls_funcs)
