from typing import Dict, Any
from logic.configuration.config_validator import IPlatSpecCfgValidatorFactory
from logic.variability import EImplementedPlatform

from logic.configuration.config_validator import AModelsConfigValidator
from logic.configuration.config_validator._private.models_validators.ollama_models_cfgvalidator import OllamaModelsConfigValidator



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