from typing import Dict, List, Tuple
from functools import reduce
from ast import Module, parse as ast_parse
from _modulecode_nodevisitor import ModuleCodeVisitor


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