from typing import Dict, Any
from .a_accessor_cfgvalidator import AAccessorConfigValidator

# ============= URL Utilities ============== #
from urllib3.util import parse_url as url_parse
# ========================================== #

from config_io.config_validator.exceptions import InvalidConfigValueError



class OllamaAccessorConfigValidator(AAccessorConfigValidator):
	"""
		Represents an `AAccessorConfigValidator` for the inference platform
        named "Ollama".
		
		The platform-specific fields are:
        
            - In "platform_options":
                
                * "api_addr" (str): The address (as a pair, separated by ":", with port) of the Ollama server to use
				* "userpass_pair" (str): The username and password pair (separated by ":") to use on the Ollama server
                * "connect_timeout" (int): The maximum wait timeout for connecting to the Ollama server (in milliseconds)
	"""
	
	def __init__(
			self,
	        config_dict: Dict[str, Any]
	):
		"""
			Creates a new OllamaGeneralConfigValidator by providing it with the Python dictionary
            of configuration settings that will be associated with this validator
            
            Parameters
            ----------
                config_dict: Dict[str, Any]
					A mixed dictionary, indexed by strings, representing the read configuration file.

			Raises
			------
                ValueError
                    Occurs if:
                    
                        - The provided dictionary is `None`
						- The provided dictionary is empty
                
                InvalidConfigFilepathError
                    Occurs if:
                    
                        - The provided configuration file path is syntactically invalid
                        - The configuration file cannot be opened
		"""
		super().__init__(config_dict)
		
		self._api_addr: str = None
		self._user_token: str = None
		self._conn_tout: int = None
	
	
	def _ap__assert_purperrors(self, config_read: Dict[str, Any]):
		return
	
	
	def _ap__assert_platspec(
			self,
			config_read: Dict[str, Any]
	):
		platf_options = config_read["platform_options"]
		self._api_addr = platf_options["api_url"]
		self._user_token = platf_options["userpass_pair"]
		self._conn_tout = platf_options["connect_timeout"]
		
		if not isinstance(self._api_addr, str):
			raise InvalidConfigValueError()
		self._assert_api_addr()
		
		if not isinstance(self._user_token, str):
			raise InvalidConfigValueError()
		self._assert_userpass_pair()
		
		if not isinstance(self._conn_tout, int):
			raise InvalidConfigValueError()
		self._pf_assert_timeout(self._conn_tout)


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	def _assert_api_addr(self):
		"""
			Check that the "api_addr" field is correct
            
            Raises
            ------
                ConfigExtraFieldsError
                    Occurs if the required format for the field is not followed
		"""
		urltoparse_str: str = self._api_addr if "://" in self._api_addr else f"http://{self._api_addr}"
		
		try:
			url_parse(urltoparse_str)
		except BaseException:
			raise InvalidConfigValueError()


	def _assert_userpass_pair(self):
		"""
			Check that the "userpass_pair" field is correct
            
            Raises
            ------
                ConfigExtraFieldsError
                    Occurs if the required format for the field is not followed
		"""
		user, token = self._user_token.strip("\n\t ").split(":")
		
		if (user == "") or (token == ""):
			raise InvalidConfigValueError()