from typing import Dict, Any
from .i_platspec_cfgvalidator_f import IPlatSpecCfgValidatorFactory
from ....variability import EImplementedPlatform

from .._private.models_validators.a_models_cfgvalidator import AModelsConfigValidator
from .._private.models_validators.ollama_models_cfgvalidator import OllamaModelsConfigValidator



class ModelsPlatSpecCfgValidatorFactory(IPlatSpecCfgValidatorFactory):
	"""
		Rappresenta un `IPlatSpecCfgValidatorFactory` per i file di configurazione
		dei Large Language Models utilizzati da GenTestsAI
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo ModelsPlatSpecCfgValidatorFactory
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