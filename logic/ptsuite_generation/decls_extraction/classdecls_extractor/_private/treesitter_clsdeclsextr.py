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
		
		self._assert_classcode_valid(class_node)
		
		self._class: TreeNode = class_node
	
	
	def class_name(self) -> str:
		class_node: TreeNode = self._get_classdef_node()
		
		return class_node.child_by_field_name("name").text.decode("utf-8")
	
	
	def method_names(self) -> List[str]:
		class_node: TreeNode = self._get_classdef_node()
		
		classbody_node: TreeNode = class_node.child_by_field_name("body")
		
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
	
	
	@classmethod
	def _assert_classcode_valid(
			cls,
			class_node: TreeNode
	):
		"""
			Verifica che il nodo fornito rappresenti una classe di Python.
			
			Se la verifica ha successo quest' operazione è equivalente ad una no-op
			
			Parameters
			----------
				class_node: TreeNode
					Un oggetto `tree_sitter.Node` rappresentante il nodo che è dovrebbe essere
					una classe di Python
			
			Raises
			------
				ValueError
					Si verifica se `class_node` non è una classe di Python
		"""
		if (class_node is None):
			raise ValueError()
		if (class_node.type == "decorated_definition"):
			if (class_node.child_by_field_name("definition").type != "class_definition"):
				raise ValueError()
		elif (class_node.type != "class_definition"):
			raise ValueError()
		
		
	def _get_classdef_node(self) -> TreeNode:
		"""
			Restituisce il nodo che contiene la definizione della classe
			senza nessun decoratore
			
			Returns
			-------
				TreeNode
					Un oggetto `tree_sitter.Node` rappresentante il nodo con la definizione
					della classe Python impostata come nodo all' attributo `self._class`
		"""
		class_node: TreeNode
		if self._class.type == "class_definition":
			class_node = self._class
		else:
			class_node = self._class.child_by_field_name("definition")
			
		return class_node