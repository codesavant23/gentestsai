from typing import Dict, Any
from .i_platspec_cfgvalidator_f import IPlatSpecCfgValidatorFactory
from llm_access.variability import EImplementedPlatform

from .._private.models_validators.a_models_cfgvalidator import AModelsConfigValidator
from .._private.models_validators.ollama_models_cfgvalidator import OllamaModelsConfigValidator



class ModelsPlatSpecCfgValidatorFactory(IPlatSpecCfgValidatorFactory):
	"""
		Represents an `IPlatSpecCfgValidatorFactory` for the configuration files
        of the Large Language Models used by GenTestsAI
	"""
	
	def __init__(self):
		"""
			Creates a new ModelsPlatSpecCfgValidatorFactory
		"""
		pass
	
	
	def create(
			self,
			config_platf: EImplementedPlatform,
			config_dict: Dict[str, Any]
	) -> AModelsConfigValidator:
		obj: AModelsConfigValidator
		match config_platf:
			case EImplementedPlatform.OLLAMA:
				obj = OllamaModelsConfigValidator(config_dict)
			
		return obj