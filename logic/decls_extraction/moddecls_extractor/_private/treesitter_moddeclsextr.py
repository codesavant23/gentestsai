from typing import List, FrozenSet
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
	
	_FUNCS_TIPOLOGY: FrozenSet[str] = {"function_definition", "async_function_definition"}
	
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
		
		self._module_source: bytes = module_code.encode("utf-8")
		self._module: TreeNode = self._py_parser.parse(self._module_source).root_node
	
	
	def set_module_code(self, module_code: str):
		super().set_module_code(module_code)
		
		self._module = self._py_parser.parse(module_code.encode()).root_node
	
	
	def extract_funcnames(self) -> List[str]:
		mod_funcsnames: List[str] = self._extract_functions(with_code=False)
				
		return mod_funcsnames
	
	
	def extract_funcs(self) -> List[str]:
		mod_funcs: List[str] = self._extract_functions(with_code=True)
		
		return mod_funcs
	
	
	def extract_classes(self) -> List[IClassDeclsExtractor]:
		mod_classes: List[IClassDeclsExtractor] = []
		class_node: TreeNode
		class_code: str
		
		for mod_stmt in self._module.named_children:
			if mod_stmt.type == "class_definition":
				self._add_class_tolist(
					mod_stmt, mod_classes
				)
			elif mod_stmt.type == "decorated_definition":
				class_node = mod_stmt.child_by_field_name("definition")
				if (class_node is not None) and (class_node.type == "class_definition"):
					self._add_class_tolist(
						mod_stmt, mod_classes
					)
		
		return mod_classes


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	def _extract_functions(self, with_code: bool) -> List[str]:
		"""
			Estrae le definizioni di funzioni che sono parte del module-file impostato.
			E' possibile scegliere se estrarre il corpo della definizione o solo il nome
			di ogni funzione trovata
			
			Parameters
			----------
				with_code: bool
					Un booleano che indica se estrarre il codice dalla definizione
					di ogni funzione
		"""
		name_only: bool = (not with_code)
		mod_funcs: List[str] = []
		inner_node: TreeNode
		
		for mod_stmt in self._module.named_children:
			if mod_stmt.type == "decorated_definition":
				inner_node = mod_stmt.child_by_field_name("definition")
				if inner_node is not None:
					self._add_iffunc_tolist(
						inner_node, mod_funcs,
						name_only=name_only
					)
			else:
				self._add_iffunc_tolist(
					mod_stmt, mod_funcs,
					name_only=name_only
				)
				
		return mod_funcs


	def _add_iffunc_tolist(
			self,
			node: TreeNode,
			list_: List[str],
			name_only: bool = True
	):
		"""
			Aggiunge l' attributo "name", o l' attributo "block", del nodo fornito alla lista data,
			se e solo se il nodo fornito è una funzione.
			
			Parameters
			----------
				node: TreeNode
					Un oggetto `TreeNode` rappresentante la possibile funzione Python di cui
					aggiungerne il nome alla lista data
				
				list_: List[str]
					Una lista di stringhe indicante la lista in cui aggiungere la definizione
					del nodo se esso rappresenta una funzione Python
					
				name_only: bool
					Opzionale. Default = `True`. Un booleano che indica se bisogna estrarre soltanto
					il nome della funzione. Se questo parametro è `False` verrà aggiunto alla lista
					tutto il codice della funzione
		"""
		needed: str
		if node.type in self._FUNCS_TIPOLOGY:
			if name_only:
				needed = node.child_by_field_name("name").text.decode("utf-8")
			else:
				needed = self._module_source[node.start_byte:node.end_byte].decode("utf-8")
			list_.append(needed)
			
			
	@classmethod
	def _add_class_tolist(
			cls,
			node: TreeNode,
			list_: List[IClassDeclsExtractor]
	):
		"""
			Crea un estrattore di codice per la classe fornita e lo aggiunge alla lista data
			
			Parameters
			----------
				node: TreeNode
					Un oggetto `TreeNode` rappresentante la classe Python di cui creare e aggiungere
					l' estrattore di codice alla lista data
				
				list_: List[str]
					Una lista di oggetti `IClassDeclsExtractor` rappresentante la lista di estrattori
					di codice di classe
		"""
		class_code: str = node.text.decode("utf-8")
		list_.append(
			TreeSitterClassDeclsExtractor(class_code)
		)