from typing import Dict, Set, Any
from .. import AJsonConfigReader

# ============= URL Utilities ============== #
from urllib3.util import parse_url as url_parse
# ========================================== #
from httpx import Timeout as HttpxTimeout
from base64 import b64encode as b64_encode

from ..exceptions import (
	FieldDoesntExistsError,
	WrongConfigFileFormatError
)



class OllamaJsonConfigReader(AJsonConfigReader):
	"""
		Rappresenta un `AJsonConfigReader` per il file di configurazione del client Ollama.
		
		Il file di configurazione letto conterrà i seguenti campi:
			- "api_url" (str): La coppia IP e porta del server Ollama da utilizzare
			- "creds" (str): Le credenziali di accesso specifiche al server di Ollama scelto
			- "timeout" (`httpx.Timeout`): L' oggetto timeout da utilizzare con il client Ollama per regolare l' attesa di connesione e di risposta
	"""
	
	_ALL_FIELDS: Set[str] = {"api_url", "userpass_pair", "connect_timeout", "response_timeout"}
	
	def __init__(
			self,
			file_path: str
	):
		"""
			Costruisce un nuovo OllamaJsonConfigReader leggendo il file di configurazione alla path
			specificata.
			
			Il formato del file deve essere un dizionario JSON composto dai seguenti campi::
			
				{
					"api_url": "<ip>:<port>",
					"userpass_pair": "<user>:<token>",
					"connect_timeout": <milliseconds>,
					"response_timeout": <milliseconds>
				}
			
			Parameters
			----------
				file_path: str
					Una stringa rappresentante la path assoluta contenente il file di configurazione
					da leggere
			
			Raises
			------
				OSError
					Si verifica se non è possibile aprire il file alla path specificata
			
				WrongConfigFileTypeError
					Si verifica se il file di configurazione dato non è un file JSON
			
				FieldDoesntExistsError
					Si verifica se il file di configurazione JSON dato ha uno più campi obbligatori mancanti
			
				WrongConfigFileFormatError
					Si verifica se:
					
						- Il file di configurazione JSON dato non è un file JSON valido
						- Il file di configurazione JSON dato non contiene un dizionario come radice
						- Il file di configurazione JSON dato non rispetta il formato specificato nel contratto di classe
		"""
		super().__init__(file_path)
		
		self._api_url: str = None
		self._user_token: str = None
		self._conn_tout: int = -1
		self._resp_tout: int = -1
	
	
	def _ap__assert_fields(
			self,
			config_read: Dict[str, Any]
	):
		config_fields: Set[str] = set(config_read.keys())
		if self._ALL_FIELDS > config_fields:
			raise FieldDoesntExistsError()
		if config_fields > self._ALL_FIELDS:
			raise WrongConfigFileFormatError()
		
		self._api_url = config_read["api_url"]
		self._user_token = config_read["userpass_pair"]
		self._conn_tout = config_read["connect_timeout"]
		self._resp_tout = config_read["response_timeout"]
		
		self._assert_api_url()
		self._assert_userpass_pair()
		self._assert_timeouts()
	
	
	def _ap__format_result(
		self,
		config_read: Dict[str, Any]
	) -> Dict[str, Any]:
		result: Dict[str, Any] = dict()
		
		result["api_url"] = self._api_url
		result["creds"] = f"Basic {b64_encode(self._user_token.encode()).decode()}"
		result["timeout"] = HttpxTimeout(
			connect=int(config_read["connect_timeout"]) / 1000.0,
			read=int(config_read["response_timeout"]) / 1000.0,
			write=None,
			pool=None
		)
		
		return result
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	def _assert_api_url(self):
		"""
			Verifica che il campo "api_url" sia corretto
			
			Raises
			------
				WrongConfigFileFormatError
					Si verifica se non è rispettato il formato richiesto per il campo
		"""
		urltoparse_str: str = self._api_url if "://" in self._api_url else f"http://{self._api_url}"
		
		try:
			url_parse(urltoparse_str)
		except BaseException as err:
			raise WrongConfigFileFormatError()


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
			raise WrongConfigFileFormatError()


	def _assert_timeouts(self):
		"""
			Verifica che i timeouts, di connessione e risposta, siano validi
			
			Raises
			------
				WrongConfigFileFormatError
					Si verifica se almeno uno dei due timeouts è minore di 1
		"""
		if (self._conn_tout < 1) or (self._resp_tout < 1):
			raise WrongConfigFileFormatError()
		