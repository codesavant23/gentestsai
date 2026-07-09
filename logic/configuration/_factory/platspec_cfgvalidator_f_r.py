from .i_platspec_cfgvalidator_f import IPlatSpecCfgValidatorFactory
from .e_platspec_purpose import EPlatSpecCfgPurpose

from .accsor_platspeccfgval_f import AccessorPlatSpecCfgValidatorFactory
from .general_platspeccfgval_f import GeneralPlatSpecCfgValidatorFactory
from .models_platspeccfgval_f import ModelsPlatSpecCfgValidatorFactory



class PlatSpecCfgValidatorFactoryResolver:
	"""
		Represents an `IPlatSpecCfgValidatorFactory` factory
	"""
	
	
	@classmethod
	def resolve(
			cls,
	        cfg_purpose: EPlatSpecCfgPurpose,
	) -> IPlatSpecCfgValidatorFactory:
		"""
			Instantiates a new `IPlatSpecCfgValidatorFactory` that produces validators for the configuration purpose,
            specific to a platform, selected by `cfg_purpose`
            
            Parameters
            ----------
				cfg_purpose: EPlatSpecCfgPurpose
                    An `EPlatSpecCfgPurpose` value representing the purpose of the configuration file,
                    associated with a specific platform, for which to obtain an `IPlatSpecCfgValidatorFactory`
					
			Returns
            -------
                IPlatSpecCfgValidatorFactory
                    An `IPlatSpecCfgValidatorFactory` object that allows you to instantiate validators
                    for the requested platform-specific configuration purpose
		"""
		obj_f: IPlatSpecCfgValidatorFactory
		
		match cfg_purpose:
			case EPlatSpecCfgPurpose.GENERAL_CONFIG:
				obj_f = GeneralPlatSpecCfgValidatorFactory()
			case EPlatSpecCfgPurpose.PLATFORM_CONFIG:
				obj_f = AccessorPlatSpecCfgValidatorFactory()
			case EPlatSpecCfgPurpose.MODELS_CONFIG:
				obj_f = ModelsPlatSpecCfgValidatorFactory()

		return obj_f
		
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================