from typing import Dict, List, Tuple
from functools import reduce
from re import search as reg_search

from tree_sitter import Language, Parser, Tree, Node as TreeNode
from tree_sitter_python import language as py_grammar


def parse_codeonly_response(resp: str) -> str:
    resp_lines: List[str] = resp.split("\n")
    code_only: str = reduce(lambda acc, line: acc + "\n" + line, resp_lines[1:(len(resp_lines) - 1)], "").lstrip("\n")
    return code_only


def extract_fmodule_code(codefile_path: str) -> Tree:
    code_mod_str: str
    with open(codefile_path, "r") as ftest:
        code_mod_str = reduce(lambda acc, x: acc + x, ftest.readlines(), "")

    py_parser: Parser = Parser(Language(py_grammar()))
    module_cst: Tree = py_parser.parse(code_mod_str.encode())
    return module_cst


def separate_fmodule_code(module_cst: Tree) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """
        Separa il codice di un modulo focale dato come argomento.
        In particolare suddivide il codice in:
            - Funzioni proprie del namespace del modulo
            - Classi proprie del namespace del modulo

        In seguito effettua una seconda suddivisione separando anche ogni metodo, di ogni classe trovata,
        associandolo alla classe in cui è definito.

        Parameters
        ----------
        module_cst: Tree
            Il Concrete Syntax Tree associato al modulo focale di cui separare le entità che lo compongono

        Returns
        -------
        Tuple[Dict[str, List[str]], Dict[str, List[str]]]
            Una tupla di 2 dizionari di liste di stringhe, indicizzati su stringhe, contenenti:

                - [0]: Il primo dizionario:

                    - "funcs": Le funzioni proprie del namespace del modulo
                    - "classes": Le classi proprie del namespace del modulo

                - [1]: Il secondo dizionario, contenente una chiave per ogni classe:
                    - "<class_name>": I metodi dichiarati nella classe <class_name>
    """
    module_entities: Dict[str, List[str]] = {
        "funcs": [],
        "classes": [],
    }
    module_classes: Dict[str, List[str]] = dict()

    cst_root: TreeNode = module_cst.root_node

    for child_node in cst_root.children:
        if child_node.type == "function_definition":
            found_func: str = child_node.text.decode()
            module_entities["funcs"].append(found_func)
        elif child_node.type == "class_definition":
            found_class: str = child_node.text.decode()
            found_clsname: str = reg_search(r"(class\s+)([a-zA-Z0-9_\-]+)", found_class.split("\n")[0]).group(2)
            module_entities["classes"].append(found_class)
            module_classes[found_clsname] =  []

            for cls_node in child_node.children:
                if cls_node.type == "block":
                    for cls_meth in cls_node.children:
                        if cls_meth.type == "function_definition":
                            found_meth: str = cls_node.text.decode()
                            module_classes[found_clsname].append(found_meth)

    return (module_entities, module_classes)


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
        elif child_node.type == "class_definition":
            for cls_node in child_node.children:
                if cls_node.type == "block":
                    for prob_func in cls_node.children:
                        ls_funcs.append(prob_func)

    return ((ls_imports, ls_fromimps), ls_funcs)
