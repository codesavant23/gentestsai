from logic.configuration.config_validator import IPlatSpecCfgValidatorFactory
from .e_platspec_purpose import EPlatSpecCfgPurpose

from .accsor_platspeccfgval_f import AccessorPlatSpecCfgValidatorFactory
from .general_platspeccfgval_f import GeneralPlatSpecCfgValidatorFactory
from .models_platspeccfgval_f import ModelsPlatSpecCfgValidatorFactory



class PlatSpecCfgValidatorFactoryResolver:
	"""
		Rappresenta una factory di `IPlatSpecCfgValidatorFactory`
	"""
	
	
	@classmethod
	def resolve(
			cls,
	        cfg_purpose: EPlatSpecCfgPurpose,
	) -> IPlatSpecCfgValidatorFactory:
		"""
			Istanzia una nuova `IPlatSpecCfgValidatorFactory` che produce validatori dello scopo
			di configurazione, specifico di una piattaforma, selezionato da `cfg_purpose`
			
			Parameters
			----------
				cfg_purpose: EPlatSpecCfgPurpose
					Un valore `EPlatSpecCfgPurpose` rappresentante lo scopo del file di configurazione,
					legato ad una specifica piattaforma, per cui ottenere un `IPlatSpecCfgValidatorFactory`
					
			Returns
			-------
				IPlatSpecCfgValidatorFactory
					Un oggetto `IPlatSpecCfgValidatorFactory` che permette di istanziare validatori
					per lo scopo di configurazione, specifico di una piattaforma, richiesto
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