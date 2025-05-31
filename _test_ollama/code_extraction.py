from typing import Dict, List, Tuple
from ast import Module, parse as ast_parse
from _modulecode_nodevisitor import ModuleCodeVisitor
from functools import reduce


def extract_focalmodule_code(codefile_path: str) -> Tuple[str, Dict[str, List[str]]]:
    """
        TODO: Finish description

        Returns
        -------
        Tuple[str, Dict[str, str]]
            Una tupla contenente:

                - L' intero codice estratto dal modulo
                - Un dizionario di stringhe, indicizzato su stringhe, contenente:

                    - "imports": Una lista di stringhe contenente tutti gli imports completi del modulo.
                    - "froms": Una lista di stringhe contenente tutti gli imports parziali del modulo.
                    - "funcs": Una lista di stringhe contenente tutti le funzioni (del modulo) estratte.
                    - "classes": Una lista di stringhe contenente tutti le definizioni di classe estratte.
    """
    result: Dict[str, List[str]] = dict()

    code_mod: Module
    code_mod_str: str
    with open(codefile_path, "r") as ftest:
        code_mod_str = reduce(lambda acc, x: acc + x, ftest.readlines(), "")
        code_mod = ast_parse(code_mod_str)

    focal_visitor: ModuleCodeVisitor = ModuleCodeVisitor()
    focal_visitor.visit(code_mod)
    mod_classes: List[str] = focal_visitor.classes_definitions()
    mod_funcs: List[str] = focal_visitor.funcs_definitions()
    mod_imports: List[str] = focal_visitor.imports()
    mod_froms: List[str] = focal_visitor.fromimports()

    result["imports"] = mod_imports
    result["froms"] = mod_froms
    result["funcs"] = mod_funcs
    result["classes"] = mod_classes

    return (code_mod_str, result)