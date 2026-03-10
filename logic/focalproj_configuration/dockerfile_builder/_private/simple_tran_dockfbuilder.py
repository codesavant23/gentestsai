from typing import List, Dict
from .. import ATransactDockfBuilder



class SimpleTransactDockfBuilder(ATransactDockfBuilder):
	"""
		Rappresenta un `ATransactDockfBuilder` implementato tramite
		una lista Python e un dizionario
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo SimpleTransactDockfBuilder
		"""
		super().__init__()
		
		self._instrs: List[str] = list()
		self._env_vars: Dict[str, str] = dict()
	
	
	def _ap__new_dockerf_spec(self):
		self._instrs.clear()
		
		del self._env_vars
		self._env_vars = dict()
	
	
	def _ap__add_instr(self, instr: str):
		self._instrs.append(instr)
	
	
	def _ap__get_dockf_body(self) -> str:
		return "\n".join(self._instrs)


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================