from typing import Dict, Any
from abc import abstractmethod
from .. import ACheckableConfigReader

# ============== JSON Utilities ============== #
from json import (
	JSONDecoder, JSONDecodeError
)
# ============================================ #

from ..exceptions import (
	WrongConfigFileTypeError,
	WrongConfigFileFormatError,
)



class AJsonConfigReader(ACheckableConfigReader):
	"""
		Rappresenta un lettore di file di configurazione JSON, di GenTestsAI, scritti in uno
		specifico formato.
		
		Ogni file di configurazione JSON letto è composto, alla radice, da un dizionario di stringhe
		con contenuto di natura potenzialmente eterogenea.
		
		La semantica del file di configurazione letto è specificata dai discendenti di questa classe astratta.
		Il formato del file di configurazione letto è specificato dai discendenti di questa classe astratta.
		Il formato del dizionario risultante è specificato dai discendenti di questa interfaccia.
	"""
	
	def __init__(
			self,
			file_path: str
	):
		"""
			Costruisce un nuovo AJsonConfigReader fornendogli la path del file di configurazione
			che verrà associato a questo lettore
			
			Parameters
			----------
				file_path: str
					Una stringa rappresentante la path assoluta contenente il file di configurazione
					da associare e leggere
			
			Raises
			------
				ValueError
					Si verifica se:
					
						- La path del file di configurazione fornita ha valore `None`
						- La path del file di configurazione fornita è una stringa vuota
						
				WrongConfigFileTypeError
					Si verifica se:
						
						- Il file di configurazione dato non è un file JSON
						- Il file non è un file JSON valido
					
				InvalidConfigFilepathError
					Si verifica se:
					
						- La path del file di configurazione fornita risulta invalida sintatticamente
						- Non è possibile aprire il file di configurazione
		"""
		super().__init__(file_path)
	
	
	def _ap__accepted_extension(self) -> str:
		return "json"
	
	
	def _ap__read_spec_config(self) -> Dict[str, Any]:
		json_dec: JSONDecoder = JSONDecoder()
		json_content: Any
		with open(self._pf__get_cfgfile_path(), "r") as fconf:
			json_content = json_dec.decode(fconf.read())
		
		if not isinstance(json_content, dict):
			raise WrongConfigFileFormatError("Il contenuto del file JSON non ha un dizionario come radice")
		
		return json_content
	
	
	def _ap__assert_type_correctness(self, cfgfile_path: str):
		json_dec: JSONDecoder = JSONDecoder()
		json_content: Any
		with open(cfgfile_path, "r") as fconf:
			try:
				json_dec.decode(fconf.read())
			except JSONDecodeError:
				raise WrongConfigFileTypeError("Il file fornito non è un file JSON valido")
	
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	

	@abstractmethod
	def _ap__assert_fields(self, config_read: Dict[str, Any]):
		pass
	
	
	@abstractmethod
	def _ap__format_result(self, config_read: Dict[str, Any]) -> Dict[str, Any]:
		pass