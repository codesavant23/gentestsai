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
	
	
	def _ap__addupd_envvar(
			self,
			var_name: str,
			value: str
	):
		self._env_vars[var_name] = value
	
	
	def _ap__rem_envvar(
			self,
			var_name: str
	):
		self._env_vars[var_name] = None
	
	
	def _ap__get_dockf_content(
			self,
			base_image: str,
			glob_args: str,
			epcmd_instrs: str = None
	) -> str:
		content: str = glob_args + "\n"

		content += base_image + "\n"
		for var_name, value in self._env_vars.items():
			content += f'ENV {var_name}={value}'
		content += "\n".join(self._instrs)
		
		return content


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================