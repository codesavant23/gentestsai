from .._private.i_classdecls_extractor import IClassDeclsExtractor
from ..._private.e_parser_tool import ECodeParserTool

from .._private.treesitter_clsdeclsextr import TreeSitterClassDeclsExtractor



class ClassDeclsExtractorFactory:
	"""
		Rappresenta una factory per ogni `IClassDeclsExtractor`
	"""
	
	
	@classmethod
	def create(
			cls,
			tool: ECodeParserTool,
	        class_code: str
	) -> IClassDeclsExtractor:
		"""
			Istanzia un nuovo estrattore di codice focale delle classi che utilizza il tool
			di parsing specificato.
			
			Parameters
			----------
				tool: ECodeParserTool
					Un valore `ECodeParserTool` rappresentante il tool di parsing che
					l' oggetto `IModuleDeclsExtractor` richiesto deve utilizzare
					
				class_code: str
					Una stringa contenente il codice della classe Python da associare
					all' estrattore
					
			Returns
			-------
				IClassDeclsExtractor
					Un oggetto `IClassDeclsExtractor` che permette di estrarre il codice focale
					della classe associata tramite il tool specificato
					
			Raises
			------
				ValueError
					Si verifica se:
						
						- Il parametro `class_code` ha valore `None`
						- Il parametro `class_code` è una stringa vuota
		"""
		obj: IClassDeclsExtractor
		match tool:
			case ECodeParserTool.TREE_SITTER:
				obj = TreeSitterClassDeclsExtractor(class_code)
		
		return obj
		
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================