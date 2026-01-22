from typing import Dict, Any
from ._a_base_cfgparser import _ABaseConfigParser

# ============== JSON Utilities ============== #
from json import (
	JSONDecoder, JSONDecodeError
)
# ============================================ #

from logic.configuration.config_parser.exceptions import (
	WrongConfigFileTypeError,
	WrongConfigFileFormatError,
)



class JsonConfigParser(_ABaseConfigParser):
	"""
		Rappresenta un `IConfigParser` per files di configurazione JSON.
		
		Ogni file di configurazione JSON letto è composto, alla radice, da un dizionario
		indicizzato da stringhe
	"""
	
	def __init__(
			self,
			file_path: str
	):
		"""
			Costruisce un nuovo JsonConfigParser fornendogli la path del file di
			configurazione che verrà associato a questo parser
			
			Parameters
			----------
				file_path: str
					Una stringa rappresentante la path assoluta contenente il file di configurazione
					da associare e parsare
			
			Raises
			------
				ValueError
					Si verifica se:
					
						- La path del file di configurazione fornita ha valore `None`
						- La path del file di configurazione fornita è una stringa vuota
						
				InvalidConfigFilepathError
					Si verifica se:
					
						- Non esiste un file alla path fornita
						- La path del file di configurazione fornita risulta invalida sintatticamente
						- Non è possibile aprire il file di configurazione
		"""
		super().__init__(file_path)
		
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
	