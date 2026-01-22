from typing import Dict, Any
from ... import AAccessorConfigValidator

# ============= URL Utilities ============== #
from urllib3.util import parse_url as url_parse
# ========================================== #

from ...exceptions import InvalidConfigValueError



class OllamaAccessorConfigValidator(AAccessorConfigValidator):
	"""
		Rappresenta un `AAccessorConfigValidator` per la piattaforma di inferenza
		di nome "Ollama".
		
		I campi specifici della piattaforma sono:
		
			- In "platform_options":
				
				* "api_addr" (str): L' indirizzo (come coppia, separata da ":", con porta) del server Ollama da utilizzare
				* "userpass_pair" (str): La coppia, separata da ":", nome utente e password da utilizzare nel server Ollama
				* "connect_timeout" (int): Il timeout di attesa massimo per la connessione al server Ollama
				* "response_timeout" (int): Il timeout di attesa massimo per il ricevimento della risposta
	"""
	
	def __init__(
			self,
	        config_dict: Dict[str, Any]
	):
		"""
			Costruisce un nuovo OllamaGeneralConfigValidator fornendogli il dizionario Python
			di configurazione che verrà associato a questo validatore
			
			Parameters
			----------
				config_dict: Dict[str, Any]
					Un dizionario variegato, indicizzato da stringhe, rappresentante il file di
					configurazione letto.
			
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il dizionario fornito ha valore `None`
						- Il dizionario fornito è vuoto
						
				InvalidConfigFilepathError
					Si verifica se:
					
						- La path del file di configurazione fornita risulta invalida sintatticamente
						- Non è possibile aprire il file di configurazione
		"""
		super().__init__(config_dict)
		
		self._api_addr: str = None
		self._userpass_pair: str = None
		self._conn_tout: int = None
		self._resp_tout: int = None
	
	
	def _ap__assert_purperrors(self, config_read: Dict[str, Any]):
		return
	
	
	def _ap__assert_platspec(
			self,
			config_read: Dict[str, Any]
	):
		self._api_addr = config_read["api_addr"]
		self._userpass_pair = config_read["userpass_pair"]
		self._conn_tout = config_read["connect_timeout"]
		self._resp_tout = config_read["response_timeout"]
		
		if not isinstance(self._api_addr, str):
			raise InvalidConfigValueError()
		self._assert_api_addr()
		
		if not isinstance(self._userpass_pair, str):
			raise InvalidConfigValueError()
		self._assert_userpass_pair()
		
		if not isinstance(self._conn_tout, int):
			raise InvalidConfigValueError()
		if not isinstance(self._resp_tout, int):
			raise InvalidConfigValueError()
		self._assert_timeouts()


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	def _assert_api_addr(self):
		"""
			Verifica che il campo "api_addr" sia corretto
			
			Raises
			------
				WrongConfigFileFormatError
					Si verifica se non è rispettato il formato richiesto per il campo
		"""
		urltoparse_str: str = self._api_addr if "://" in self._api_addr else f"http://{self._api_addr}"
		
		try:
			url_parse(urltoparse_str)
		except BaseException as err:
			raise InvalidConfigValueError()


	def _assert_userpass_pair(self):
		"""
			Verifica che il campo "userpass_pair" sia corretto
			
			Raises
			------
				WrongConfigFileFormatError
					Si verifica se non è rispettato il formato richiesto per il campo
		"""
		user, token = self._user_token.strip("\n\t ").split(":")
		
		if (user == "") or (token == ""):
			raise InvalidConfigValueError()


	def _assert_timeouts(self):
		"""
			Verifica che i timeouts, di connessione e risposta, siano validi
			
			Raises
			------
				WrongConfigFileFormatError
					Si verifica se almeno uno dei due timeouts è minore di 1
		"""
		if (self._conn_tout < 1) or (self._resp_tout < 1):
			raise InvalidConfigValueError()