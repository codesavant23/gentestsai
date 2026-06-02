from typing import Dict, Any
from abc import ABC, abstractmethod
from logic.configuration.config_validator import IConfigValidator

from logic.variability import EImplementedPlatform



class IPlatSpecCfgValidatorFactory(ABC):
	"""
		Rappresenta una factory per ogni `IConfigValidator` che rappresenta
		un file di configurazione legato ad una specifica piattaforma di inferenza
		
		Lo scopo del file di configurazione validabile è specificato dai discendenti di questa interfaccia.
	"""
	
	
	@abstractmethod
	def create(
			self,
			config_platf: EImplementedPlatform,
	        config_dict: Dict[str, Any]
	) -> IConfigValidator:
		"""
			Istanzia un nuovo validatore di files di configurazione, dello scopo descritto dai discendenti,
			legato alla piattaforma di inferenza richiesta
			
			Parameters
			----------
				config_platf: EImplementedPlatform
					Un valore `EImplementedPlatform` rappresentante la piattaforma di inferenza a cui
					è legato l' oggetto `IConfigValidator` richiesto
					
				config_dict: Dict[str, Any]
					Un dizionario variegato, indicizzato da stringhe, contenente il file di configurazione
					letto da assegnare al validatore che verrà istanziato
					
			Returns
			-------
				IConfigValidator
					Un oggetto `IConfigValidator`, legato alla piattaforma specificata dai discendenti
					di questa interfaccia, che valida il file di configurazione con lo scopo richiesto
					
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il dizionario fornito ha valore `None`
						- Il dizionario fornito è vuoto
		"""
		pass
		
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================