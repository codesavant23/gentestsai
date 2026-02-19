from typing import Dict, Set, Any, Tuple
from abc import abstractmethod
from .._a_platspec_cfgvalidator import _APlatSpecConfigValidator

"""
	from httpx import Timeout as HttpxTimeout
	from base64 import b64encode as b64_encode
"""

from .....variability import EImplementedPlatform

from ...exceptions import InvalidConfigValueError



class AAccessorConfigValidator(_APlatSpecConfigValidator):
	"""
		Rappresenta un `IConfigValidator` per il file di configurazione della piattaforma
		di inferenza da utilizzare.
		
		Il file di configurazione letto è un dizionario contenente:
		
			- "platform" (str): Il naming della piattaforma di inferenza da utilizzare
			- "platform_options" (Dict[str, Any]): Dizionario che contiene i parametri relativi ad ogni progetto focale.
			  Ciò che contiene è relativo alla piattaforma di inferenza ed è specificato dai discendenti
			  di questa classe astratta.
			- "response_timeout" (int): Il timeout di attesa massimo per il ricevimento della risposta (in millisecondi)
		
		La piattaforma di inferenza specifica è descritta dai discendenti di questa classe astratta
	"""
	
	_ALL_FIELDS: Set[str] = {"platform", "platform_options", "response_timeout"}
	
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
		self._resp_tout: int = -1
	
	
	def _ap__fields(self) -> Tuple[Set[str], Set[str]]:
		return (self._ALL_FIELDS, set())
	
	
	def _ap__assert_mandatory(self, config_read: Dict[str, Any]):
		platform: str = config_read["platform"]
		if not isinstance(platform, str):
			raise InvalidConfigValueError()
		
		self._resp_tout = config_read["response_timeout"]
		if not isinstance(self._resp_tout, int):
			raise InvalidConfigValueError()
		self._pf_assert_timeout(self._resp_tout)
		
		platform = platform.lower().upper()
		if not (platform in EImplementedPlatform.__members__):
			raise InvalidConfigValueError(f'La piattaforma {platform} non è implementata')
	
	
	def _ap__assert_optional(self, config_read: Dict[str, Any]):
		return
	
	
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

	
	@classmethod
	def _pf_assert_timeout(cls, timeout: int):
		"""
			Verifica che il timeout fornito sia valido
			
			Raises
			------
				ConfigExtraFieldsError
					Si verifica se il timeout fornito è minore di 1
		"""
		if (timeout < 1):
			raise InvalidConfigValueError()