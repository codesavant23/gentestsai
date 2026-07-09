from typing import Dict, Any
from .i_platspec_cfgvalidator_f import IPlatSpecCfgValidatorFactory
from llm_access.variability import EImplementedPlatform

from .._private.general_validators.a_general_cfgvalidator import AGeneralConfigValidator
from .._private.general_validators.ollama_general_cfgvalidator import OllamaGeneralConfigValidator



class GeneralPlatSpecCfgValidatorFactory(IPlatSpecCfgValidatorFactory):
	"""
		Represents an `IPlatSpecCfgValidatorFactory` for the configuration files
        of the general parameters used by GenTestsAI
	"""
	
	def __init__(self):
		"""
			Creates a new GeneralPlatSpecCfgValidatorFactory
		"""
		pass
	
	
	def create(
			self,
			config_platf: EImplementedPlatform,
			config_dict: Dict[str, Any]
	) -> AGeneralConfigValidator:
		obj: AGeneralConfigValidator
		match config_platf:
			case EImplementedPlatform.OLLAMA:
				obj = OllamaGeneralConfigValidator(config_dict)
			
		return obj