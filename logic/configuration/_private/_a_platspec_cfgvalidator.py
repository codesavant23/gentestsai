from typing import Dict, Set, Tuple, Any
from abc import abstractmethod
from config_io.config_validator._private._a_base_cfgvalidator import _ABaseConfigValidator



class _APlatSpecConfigValidator(_ABaseConfigValidator):
	"""
		Represents an `IConfigValidator` for configuration files whose scope defines fields related to a specific platform.
        
        The scope of the validated configuration file is specified by the descendants of this abstract class.
        The specific inference platform is described by the descendants of this abstract class.
	"""
	
	def __init__(
			self,
			config_dict: Dict[str, Any]
	):
		"""
			Creates a new _APlatSpecConfigValidator by passing it the Python configuration dictionary
            that will be associated with this validator
            
            Parameters
            ----------
				config_dict: Dict[str, Any]
                    A mixed dictionary, indexed by strings, representing the read configuration file.
			
			Raises
            ------
                ValueError
                    Occurs if:
                    
                        - The provided dictionary has a value of `None`
                        - The provided dictionary is empty
		"""
		super().__init__(config_dict)
	
	
	def validate_sem(self):
		super().validate_sem()
		
		self._ap__assert_platspec(self._pf__get_dict())
	
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	
	
	@abstractmethod
	def _ap__assert_platspec(self, config_read: Dict[str, Any]):
		"""
			Checks the validity of the field values related to the inference platform
            specified by the subclasses of this abstract class.
            
            If validation is successful, this operation must be equivalent to a no-op.
        
            The following is guaranteed within this method:
			
				- That all required fields, not specific to the inference platform,
                  exist and are semantically correct
                - That the optional fields, if they exist, not specific to the inference platform,
                  are semantically correct
				  
			Parameters
            ----------
                config_read: Dict[str, Any]
                    A mixed dictionary, indexed by strings, representing the
                    configuration file read
			
			Raises
            ------
                InvalidConfigValueError
                    Occurs if the semantics of one or more fields are correct but there is a
                    specific error declared by the descendants of this abstract class
		"""
		pass
	
	
	@abstractmethod
	def _ap__fields(self) -> Tuple[Set[str], Set[str]]:
		pass
	
	
	@abstractmethod
	def _ap__assert_mandatory(self, config_read: Dict[str, Any]):
		pass
	
	
	@abstractmethod
	def _ap__assert_optional(self, config_read: Dict[str, Any]):
		pass
	
	
	@abstractmethod
	def _ap__assert_purperrors(self, config_read: Dict[str, Any]):
		pass
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================