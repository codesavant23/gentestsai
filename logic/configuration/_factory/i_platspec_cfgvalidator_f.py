from typing import Dict, Any
from abc import ABC, abstractmethod
from config_io.config_validator import IConfigValidator

from llm_access.variability import EImplementedPlatform



class IPlatSpecCfgValidatorFactory(ABC):
	"""
		Represents a factory for each `IConfigValidator`, which represents
        a configuration file associated with a specific inference platform
        
        The purpose of the validatable configuration file is specified by the descendants of this interface.
	"""
	
	
	@abstractmethod
	def create(
			self,
			config_platf: EImplementedPlatform,
	        config_dict: Dict[str, Any]
	) -> IConfigValidator:
		"""
			Instantiates a new configuration file validator, with the scope described by its descendants,
            associated with the requested inference platform
            
            Parameters
            ----------
				config_platf: EImplementedPlatform
                    An `EImplementedPlatform` value representing the inference platform to which
                    the requested `IConfigValidator` object is bound
					
				config_dict: Dict[str, Any]
                    A mixed dictionary, indexed by strings, containing the configuration file
                    to be assigned to the validator that will be instantiated
                    
            Returns
            -------
				IConfigValidator
                    An `IConfigValidator` object, bound to the platform specified by the subclasses
                    of this interface, which validates the configuration file for the requested purpose
					
			Raises
            ------
                ValueError
                    Occurs if:
                    
                        - The provided dictionary is `None`
                        - The provided dictionary is empty
		"""
		pass
		
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================