from typing import Dict, Any
from logic.configuration.config_validator import IPlatSpecCfgValidatorFactory
from logic.variability import EImplementedPlatform

from logic.configuration.config_validator import AGeneralConfigValidator
from logic.configuration.config_validator._private.general_validators.ollama_general_cfgvalidator import OllamaGeneralConfigValidator



class GeneralPlatSpecCfgValidatorFactory(IPlatSpecCfgValidatorFactory):
	"""
		Rappresenta un `IPlatSpecCfgValidatorFactory` per i file di configurazione
		dei parametri generali utilizzati da GenTestsAI
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo GeneralPlatSpecCfgValidatorFactory
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