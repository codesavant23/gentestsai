from typing import Dict, Set, Any, Tuple
from abc import abstractmethod
from .._a_platspec_cfgvalidator import _APlatSpecConfigValidator

from llm_access.variability import EImplementedPlatform

from config_io.config_validator.exceptions import InvalidConfigValueError



class AAccessorConfigValidator(_APlatSpecConfigValidator):
	"""
		Represents an `IConfigValidator` for the configuration file of the inference platform to be used.
		
		The configuration file read is a dictionary containing:
        
            - "platform" (str): The name of the inference platform to use
            - "platform_options" (Dict[str, Any]): A dictionary containing the inference platform parameters.
			  Its contents are specific to the inference platform and are specified by the subclasses
              of this abstract class.
            - "response_timeout" (int): The maximum wait timeout for receiving a response (in milliseconds)
        
        The specific inference platform is described by the subclasses of this abstract class
	"""
	
	_ALL_FIELDS: Set[str] = {"platform", "platform_options", "response_timeout"}
	
	def __init__(
			self,
			config_dict: Dict[str, Any]
	):
		"""
			Creates a new AccessorConfigValidator by providing it with the Python configuration dictionary
            that will be associated with this validator
            
            Parameters
            ----------
				config_dict: Dict[str, Any]
                    A mixed dictionary, indexed by strings, representing the configuration file
                    that was read
			
			Raises
            ------
                ValueError
                    Occurs if:
                    
                        - The provided dictionary is `None`
                        - The provided dictionary is empty
		"""
		super().__init__(config_dict)
	
	
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
			Checks whether the provided timeout is valid
            
            Raises
            ------
                ConfigExtraFieldsError
                    Checks whether the provided timeout is less than 1
		"""
		if (timeout < 1):
			raise InvalidConfigValueError()