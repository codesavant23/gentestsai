from typing import List
from .. import IClassDeclsExtractor

from tree_sitter import (
	Language, Parser, Tree,
	Node as TreeNode
)
from tree_sitter_python import language as py_grammar



class TreeSitterClassDeclsExtractor(IClassDeclsExtractor):
	"""
		Rappresenta un `IClassDeclsExtractor` che è implementato tramite l'utilizzo
		della libreria `tree-sitter` di Python
	"""
	
	def __init__(
			self,
			class_code: str
	):
		"""
			Costruisce un nuovo TreeSitterClassDeclsExtractor
			
			Parameters
			----------
				class_code: str
					Una stringa contenente il codice della classe Python di cui
					estrarre le dichiarazioni dei metodi
			
			Raises
			------
				ValueError
					Si verifica se il codice fornito non è una definizione di una classe Python
		"""
		
		py_parser: Parser = Parser(Language(py_grammar()))
		module_cst: Tree = py_parser.parse(class_code.encode())
		
		class_node: TreeNode = module_cst.root_node.named_child(0)
		if class_node.type != "class_definition":
			raise ValueError()
		
		self._class: TreeNode = class_node
	
	
	def class_name(self) -> str:
		return self._class.child_by_field_name("name").text.decode("utf-8")
	
	
	def method_names(self) -> List[str]:
		classbody_node: TreeNode = self._class.child_by_field_name("body")
		
		if classbody_node is None:
			return []
		
		class_methods: List[str] = []
		poss_method: TreeNode
		meth_name: str
		for stmt in classbody_node.named_children:
			if stmt.type == "function_definition":
				# Estrazione metodo classico
				meth_name = stmt.child_by_field_name("name").text.decode("utf-8")
				class_methods.append(meth_name)
				
			elif stmt.type == "decorated_definition":
				# Estrazione metodo decorato
				poss_method = stmt.child_by_field_name("definition")
				if poss_method is not None:
					if poss_method.type == "function_definition":
						meth_name = poss_method.child_by_field_name("name").text.decode("utf-8")
						class_methods.append(meth_name)
				
		return class_methods