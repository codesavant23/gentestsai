from typing import Dict, Any
from ._a_base_cfgparser import _ABaseConfigParser

# ============== JSON Utilities ============== #
from json import (
	JSONDecoder, JSONDecodeError
)
# ============================================ #

from ..exceptions import (
	WrongConfigFileTypeError,
	WrongConfigFileFormatError,
)



class JsonConfigParser(_ABaseConfigParser):
	"""
		Rappresenta un `IConfigParser` per files di configurazione JSON.
		
		Ogni file di configurazione JSON letto è composto, alla radice, da un dizionario
		indicizzato da stringhe
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo JsonConfigParser
		"""
		super().__init__()
		
		self._json_dec: JSONDecoder = JSONDecoder()
	
	
	def _p__file_extension(self) -> str:
		return "json"
	
	
	def _ap__read_spec(self, cfg_path: str) -> Dict[str, Any]:
		json_content: Any
		with open(cfg_path, "r") as fconf:
			try:
				json_content = self._json_dec.decode(fconf.read())
			except JSONDecodeError:
				raise WrongConfigFileTypeError("Il file fornito non è un file JSON valido")
			
		if not isinstance(json_content, dict):
			raise WrongConfigFileFormatError("Il contenuto del file JSON non ha un dizionario come radice")
		
		return json_content
	
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	