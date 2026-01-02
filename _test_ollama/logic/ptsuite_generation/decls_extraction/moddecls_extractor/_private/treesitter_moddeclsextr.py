from typing import List
from .. import AMutableModuleDeclsExtractor

from tree_sitter import (
	Language, Parser,
	Node as TreeNode
)
from tree_sitter_python import language as py_grammar

from ...classdecls_extractor import (
	IClassDeclsExtractor,
	TreeSitterClassDeclsExtractor
)



class TreeSitterModuleDeclsExtractor(AMutableModuleDeclsExtractor):
	"""
		Rappresenta un `AMutableModuleDeclsExtractor` che è implementato tramite l'utilizzo
		della libreria `tree-sitter` di Python
	"""
	
	def __init__(
			self,
			module_code: str
	):
		"""
			Costruisce un nuovo TreeSitterModuleDeclsExtractor fornendo il primo module-file
			da cui estrarne le dichiarazioni di funzioni e classi
			
			Parameters
			----------
				module_code: str
					Una stringa contenente il codice del module-file di cui estrarre
					le dichiarazioni
					
			Raises
			------
				ValueError
					Si verifica se:
					
						- La stringa fornita è vuota
						- E' stato fornito `None` come valore di `module_code`
						
				IncorrectModuleCodeError
					Si verifica se il codice del modulo contiene errori da un punto di vista sintattico
		"""
		super().__init__(module_code)
		
		self._py_parser: Parser = Parser(Language(py_grammar()))
		
		self._module: TreeNode = self._py_parser.parse(module_code.encode()).root_node
	
	
	def set_module_code(self, module_code: str):
		super().set_module_code(module_code)
		
		self._module = self._py_parser.parse(module_code.encode()).root_node
	
	
	def extract_funcs(self) -> List[str]:
		mod_funcs: List[str] = []
		inner_node: TreeNode
		
		for mod_stmt in self._module.named_children:
			if mod_stmt.type == "decorated_definition":
				inner_node = mod_stmt.child_by_field_name("definition")
				if inner_node is not None:
					self._add_iffunc_tolist(
						inner_node, mod_funcs
					)
			else:
				self._add_iffunc_tolist(
					mod_stmt, mod_funcs
				)
				
		return mod_funcs
	
	
	def extract_classes(self) -> List[IClassDeclsExtractor]:
		mod_classes: List[IClassDeclsExtractor] = []
		class_code: str
		
		for mod_stmt in self._module.named_children:
			if mod_stmt.type == "class_definition":
				class_code = mod_stmt.text.decode("utf-8")
				mod_classes.append(
					TreeSitterClassDeclsExtractor(class_code)
				)
		
		return mod_classes


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	@classmethod
	def _add_iffunc_tolist(
			cls,
			node: TreeNode,
			list_: List[str]
	):
		"""
			Aggiunge l' attributo "name" del nodo fornito, alla lista data, se e solo se
			il nodo fornito è una funzione.
			
			Parameters
			----------
				node: TreeNode
					Un oggetto `TreeNode` rappresentante la possibile funzione Python di cui
					aggiungerne il nome alla lista data
				
				list_: List[str]
					Una lista di stringhe indicante la lista in cui aggiungere il "name" del nodo
					se esso rappresenta una funzione Python.
		"""
		func_name: str
		if node.type == "function_definition":
			func_name = node.child_by_field_name("name").text.decode("utf-8")
			list_.append(func_name)