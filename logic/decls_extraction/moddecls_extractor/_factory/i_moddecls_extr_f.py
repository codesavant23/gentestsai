from .._private.i_moddecls_extractor import IModuleDeclsExtractor

from ..._private.e_parser_tool import ECodeParserTool



class IModuleDeclsExtractorFactory:
	"""
		Rappresenta una factory per ogni `IModuleDeclsExtractor`.
		
		Le proprietà astratte caratteristiche delle implementazioni specifiche istanziate, sono
		descritte dai discendenti di questa interfaccia.
	"""
	
	
	def create(
			self,
			tool: ECodeParserTool,
	        module_code: str
	) -> IModuleDeclsExtractor:
		"""
			Istanzia un nuovo estrattore di codice focale dei moduli che utilizza il tool di parsing
			specificato
			
			Parameters
			----------
				tool: ECodeParserTool
					Un valore `ECodeParserTool` rappresentante il tool di parsing che
					l' oggetto `IModuleDeclsExtractor` richiesto deve utilizzare
					
				module_code: str
					Una stringa contenente il codice del modulo Python da associare
					all' estrattore
					
			Returns
			-------
				IModuleDeclsExtractor
					Un oggetto `IModuleDeclsExtractor` che permette di estrarre il codice focale
					del modulo associato tramite il tool specificato
					
			Raises
			------
				ValueError
					Si verifica se:
						
						- Il parametro `module_code` ha valore `None`
						- Il parametro `module_code` è una stringa vuota
						
				NotImplementedError
					Si verifica se l' estrattore di moduli richiesto non è implementato, in GenTestsAI,
					per le proprietà astratte caratteristiche degli `IModuleDeclsExtractor` istanziati
					specificate dai discendenti di questa interfaccia
		"""
		pass
		
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================