from typing import Dict, Any
from .i_platspec_cfgvalidator_f import IPlatSpecCfgValidatorFactory
from llm_access.variability import EImplementedPlatform

from .._private.accessor_validators.a_accessor_cfgvalidator import AAccessorConfigValidator
from .._private.accessor_validators.ollama_accssor_cfgvalidator import OllamaAccessorConfigValidator



class AccessorPlatSpecCfgValidatorFactory(IPlatSpecCfgValidatorFactory):
	"""
		Represents an `IPlatSpecCfgValidatorFactory` for the configuration files
        of the inference platform parameters used by GenTestsAI
	"""
	
	def __init__(self):
		"""
			Creates a new AccessorPlatSpecCfgValidatorFactory
		"""
		pass
	
	
	def create(
			self,
			config_platf: EImplementedPlatform,
			config_dict: Dict[str, Any]
	) -> AAccessorConfigValidator:
		obj: AAccessorConfigValidator
		match config_platf:
			case EImplementedPlatform.OLLAMA:
				obj = OllamaAccessorConfigValidator(config_dict)
			
		return obj