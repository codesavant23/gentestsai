from typing import Dict, Any
from .i_platspec_cfgvalidator_f import IPlatSpecCfgValidatorFactory
from ....variability import EImplementedPlatform

from .._private.accessor_validators.a_accessor_cfgvalidator import AAccessorConfigValidator
from .._private.accessor_validators.ollama_accssor_cfgvalidator import OllamaAccessorConfigValidator



class AccessorPlatSpecCfgValidatorFactory(IPlatSpecCfgValidatorFactory):
	"""
		Rappresenta un `IPlatSpecCfgValidatorFactory` per i file di configurazione
		dei parametri della piattaforma di inferenza usata da GenTestsAI
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo AccessorPlatSpecCfgValidatorFactory
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