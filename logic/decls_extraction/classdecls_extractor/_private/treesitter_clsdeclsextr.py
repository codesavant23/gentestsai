from typing import List, FrozenSet
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
	
	_METHS_TIPOLOGY: FrozenSet[str] = { "function_definition", "async_function_definition" }
	
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
					Si verifica se :
						
						- Il parametro `class_code` ha valore `None`
						- Il parametro `class_code` è una stringa vuota
						- Il codice fornito non è una definizione di una classe Python
		"""
		if (class_code is None) or (class_code == ""):
			raise ValueError()
		
		py_parser: Parser = Parser(Language(py_grammar()))
		
		self._module_source: bytes = class_code.encode("utf-8")
		module_cst: Tree = py_parser.parse(self._module_source)
		
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
		
		class_methods: List[str] = self._extract_methods(classbody_node, with_code=False)
		return class_methods
	
	
	def methods(self) -> List[str]:
		class_node: TreeNode = self._get_classdef_node()
		
		classbody_node: TreeNode = class_node.child_by_field_name("body")
		
		if classbody_node is None:
			return []
		
		class_methods: List[str] = self._extract_methods(classbody_node, with_code=True)
		return class_methods
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================
	
	
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
	
	
	def _extract_methods(
			self,
			classbody_node: TreeNode,
			with_code: bool
	) -> List[str]:
		"""
			Estrae le definizioni di funzioni che sono parte del module-file impostato.
			E' possibile scegliere se estrarre il corpo della definizione o solo il nome
			di ogni metodo trovato
			
			Parameters
			----------
				with_code: bool
					Un booleano che indica se estrarre il codice dalla definizione
					di ogni metodo
		"""
		name_only: bool = (not with_code)
		class_methods: List[str] = []
		poss_method: TreeNode
		meth_name: str
		for stmt in classbody_node.named_children:
			poss_method = None
			
			if stmt.type == "decorated_definition":
				# Estrazione metodo decorato
				poss_method = stmt.child_by_field_name("definition")
			else:
				# Estrazione metodo classico
				poss_method = stmt
				
			if poss_method is not None:
				self._add_ifmeth_tolist(stmt, class_methods, name_only)
		
		return class_methods
	
	
	def _add_ifmeth_tolist(
			self,
			node: TreeNode,
			list_: List[str],
			name_only: bool = True
	):
		"""
			Aggiunge l' attributo "name", o l' attributo "block", del nodo fornito alla lista data,
			se e solo se il nodo fornito è un metodo.
			
			Parameters
			----------
				node: TreeNode
					Un oggetto `TreeNode` rappresentante il possibile metodo Python di cui
					aggiungerne il nome alla lista data
				
				list_: List[str]
					Una lista di stringhe indicante la lista in cui aggiungere la definizione
					del nodo se esso rappresenta un metodo Python
					
				name_only: bool
					Opzionale. Default = `True`. Un booleano che indica se bisogna estrarre soltanto
					il nome del metodo. Se questo parametro è `False` verrà aggiunto alla lista
					tutto il codice del metodo
		"""
		needed: str
		if node.type in self._METHS_TIPOLOGY:
			if name_only:
				needed = node.child_by_field_name("name").text.decode("utf-8")
			else:
				needed = self._module_source[node.start_byte:node.end_byte].decode("utf-8")
			list_.append(needed)
		
		
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