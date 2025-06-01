from typing import List, Set
from functools import reduce
from re import Match, search as reg_search


class ModuleTestSuite:
    """
        TODO: Contratto
    """

    def __init__(self,
                 imports: List[str],
                 fromimports: List[str],
                 functions: List[str],
                 classes: List[str]):
        self._imports: List[str] = imports
        self._froms: List[str] = fromimports
        self._funcs: List[str] = functions
        self._classes: List[str] = classes


    def add_import(self, import_stmt: str):
        self._imports.append(import_stmt)


    def add_fromimport(self, fromimport: str):
        self._froms.append(fromimport)


    def add_func(self, function: str):
        self._funcs.append(function)


    def add_class(self, py_class: str):
        self._classes.append(py_class)


    def test_suite(self) -> str:
        imports: str = self._combine_imports()
        fromimports: str = self._combine_fromimports()
        funcs: str = self._combine_funcs()
        classes: str = self._combine_classes()

        test_suite: str = \
            imports + "\n" + fromimports + \
            "\n\n" + funcs + \
            "\n\n\n" + classes

        return test_suite


    def _combine_imports(self) -> str:
        module_imports: List[str] = list(set(self._imports))
        result_imports: Set[str] = set()
        import_patt: str = r"^import (?P<namespace>[A-z0-9_\.\-]+)(?: as (?P<alias>[A-z0-9_\-]+))?$"

        for imp in module_imports:
            for line in imp.split("\n"):
                match: Match[str] = reg_search(import_patt, line)
                if match is None:
                    ValueError("At least one line in the imports given is not an import")
                result_imports.add(line)

        return reduce(lambda acc,x: acc + "\n" + x, result_imports, "").strip(" \t\n")


    def _combine_fromimports(self) -> str:
        module_fromimports: List[str] = list(set(self._froms))
        result_fromimports: List[str] = []
        fromimport_namesp_patt: str = r"^from (?P<namespace>[A-z0-9_\.\-]+)"
        fromimport_patt: str = fromimport_namesp_patt + r" import (?P<imports>(?:[A-z0-9_\-]+(?: as [A-z0-9_\-]+)?(?: *, *)?)+)"

        for fromimport in module_fromimports:
            for line in fromimport.split("\n"):
                match: Match[str] = reg_search(fromimport_patt, line)
                currline_namesp: str = match.group("namespace")
                chosen_namesps: List[str] = list(map(lambda x: reg_search(fromimport_namesp_patt, x).group("namespace"), result_fromimports))

                if currline_namesp in chosen_namesps:
                    dest_idx: int = chosen_namesps.index(currline_namesp)
                    line_imports: str = match.group("imports")
                    result_fromimports[dest_idx] += ("," + line_imports)
                else:
                    result_fromimports.append(line)

        return reduce(lambda acc,x: acc + "\n" + x, result_fromimports, "").strip(" \t\n")


    def _combine_funcs(self) -> str:
        funcs: str = ""
        for func in self._funcs:
            funcs += "\n\n" + func
        return funcs.strip(" \t\n")


    def _combine_classes(self) -> str:
        classes: str = ""
        for cls in self._classes:
            classes += "\n\n" + cls
        return classes.strip(" \t\n")