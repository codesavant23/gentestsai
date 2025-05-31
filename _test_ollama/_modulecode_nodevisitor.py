from typing import List
from ast import NodeVisitor, FunctionDef, ClassDef, Import, ImportFrom
from ast import unparse as ast_unparse


class ModuleCodeVisitor(NodeVisitor):
    """
        Rappresenta un NodeVisitor che estrae il codice relativo a funzioni e classi definite in
        un determinato modulo di cui si fornisce l' ast.AST.
        Questo NodeVisitor estrae inoltre tutti gli import utilizzati nel modulo fornito
        per la visita.

        La principale operazione da utilizzare, come ogni NodeVisitor, è la `.visit(ast.AST)`
        per effettuare l' estrazione.

        In seguito bisogna utilizzare i metodi `funcs_definitions()` e `classes_definitions()` per
        ottenere, rispettivamente, le funzioni e le classi definite nel modulo corrispondente all'
        ast.AST dato.
        Mentre per ottenere gli imports si utilizzano i metodi `imports` e `fromimports()`.
    """

    def __init__(self):
        self._in_class = False
        self._funcs: List[FunctionDef] = []
        self._classes: List[ClassDef] = []
        self._imports: List[Import] = []
        self._froms: List[Import] = []


    def visit_Import(self, node: Import):
        self._imports.append(node)


    def visit_ImportFrom(self, node: ImportFrom):
        self._froms.append(node)


    def visit_ClassDef(self, node: ClassDef):
        self._in_class = True
        self._classes.append(node)
        # Visito l' interno della classe
        self.generic_visit(node)
        self._in_class = False


    def visit_FunctionDef(self, node: FunctionDef):
        if not self._in_class:
            self._funcs.append(node)


    def classes_definitions(self) -> List[str]:
        result: List[str] = []
        for cls in self._classes:
            result.append(ast_unparse(cls))
        return result


    def funcs_definitions(self) -> List[str]:
        result: List[str] = []
        for func in self._funcs:
            result.append(ast_unparse(func))
        return result


    def imports(self) -> List[str]:
        result: List[str] = []
        for imp in self._imports:
            result.append(ast_unparse(imp))
        return result


    def fromimports(self) -> List[str]:
        result: List[str] = []
        for fromimp in self._froms:
            result.append(ast_unparse(fromimp))
        return result