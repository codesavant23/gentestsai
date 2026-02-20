from .. import ISyntacticChecker

from .e_synt_chker_tool import ESyntCheckerTool
from .._private.pycomp_syntcker import PyCompileSyntChecker



class SyntacticCheckerFactory:
	"""
		Rappresenta una factory per ogni `ISyntacticChecker`
	"""
	
	
	@classmethod
	def create(
			cls,
			tool: ESyntCheckerTool,
	) -> ISyntacticChecker:
		"""
			Istanzia un nuovo verificatore della correttezza sintattica che utilizza
			il tool di verifica specificato
			
			Parameters
			----------
				tool: ESyntCheckerTool
					Un valore `ESyntCheckerTool` rappresentante il tool di verifica che
					l' oggetto `ISyntacticChecker` deve utilizzare
					
			Returns
			-------
				ISyntacticChecker
					Un oggetto `ISyntacticChecker` che permette la verifica di correttezza 
					sintattica di una test-suite parziale utilizzando il tool di verifica
					specificato
		"""
		obj: ISyntacticChecker
		match tool:
			case ESyntCheckerTool.PYCOMPILE:
				obj = PyCompileSyntChecker()
			
		return obj
		
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================