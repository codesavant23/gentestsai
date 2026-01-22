from typing import Dict, Set, Any, Tuple
from abc import abstractmethod
from .._a_platspec_cfgvalidator import _APlatSpecConfigValidator

from ... import EImplementedPlatform

"""
	from httpx import Timeout as HttpxTimeout
	from base64 import b64encode as b64_encode
"""

from ...exceptions import InvalidConfigValueError



class AAccessorConfigValidator(_APlatSpecConfigValidator):
	"""
		Rappresenta un `IConfigValidator` per il file di configurazione della piattaforma
		di inferenza da utilizzare.
		
		Il file di configurazione letto è un dizionario contenente:
		
			- "platform" (str): Il naming della piattaforma di inferenza da utilizzare
			- "platform_options" (Dict[str, str]): Dizionario che contiene i parametri relativi ad ogni progetto focale.
			  Ciò che contiene è relativo alla piattaforma di inferen
		
		La piattaforma di inferenza specifica è descritta dai discendenti di questa classe astratta
	"""
	
	_ALL_FIELDS: Set[str] = {"platform", "platform_options"}
	
	def __init__(
			self,
			config_dict: Dict[str, Any]
	):
		"""
			Costruisce un nuovo AccessorConfigValidator fornendogli il dizionario Python di configurazione
			che verrà associato a questo validatore
			
			Parameters
			----------
				config_dict: Dict[str, Any]
					Un dizionario variegato, indicizzato da stringhe, rappresentante il file di
					configurazione letto
			
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il dizionario fornito ha valore `None`
						- Il dizionario fornito è vuoto
		"""
		super().__init__(config_dict)
		
		self._api_url: str = None
		self._user_token: str = None
		self._conn_tout: int = -1
		self._resp_tout: int = -1
	
	
	def _ap__fields(self) -> Tuple[Set[str], Set[str]]:
		return (self._ALL_FIELDS, set())
	
	
	def _ap__assert_mandatory(self, config_read: Dict[str, Any]):
		platform: str = config_read["platform"]
		if not isinstance(platform, str):
			raise InvalidConfigValueError()
			
		platform = platform.lower().upper()
		if not (platform in EImplementedPlatform.__members__):
			raise InvalidConfigValueError(f'La piattaforma {platform} non è implementata')
	
	
	def _ap__assert_optional(self, config_read: Dict[str, Any]):
		return
	
	
	def _ap__assert_fields(
			self,
			config_read: Dict[str, Any]
	):
		config_fields: Set[str] = set(config_read.keys())
		
		self._api_url = config_read["api_url"]
		self._user_token = config_read["userpass_pair"]
		self._conn_tout = config_read["connect_timeout"]
		self._resp_tout = config_read["response_timeout"]
		

	"""
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
	"""
	
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	
	
	@abstractmethod
	def _ap__assert_platspec(self, config_read: Dict[str, Any]):
		pass
	
	
	@abstractmethod
	def _ap__assert_purperrors(self, config_read: Dict[str, Any]):
		pass
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================



		