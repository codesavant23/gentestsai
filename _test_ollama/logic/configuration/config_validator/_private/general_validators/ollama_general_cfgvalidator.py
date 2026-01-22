from typing import Dict, Any
from ... import AGeneralConfigValidator

from ...exceptions import InvalidConfigValueError



class OllamaGeneralConfigValidator(AGeneralConfigValidator):
	"""
		Rappresenta un `AGeneralConfigValidator` per la piattaforma di inferenza
		di nome "Ollama".
		
		I campi specifici della piattaforma sono:
		
			- In "default_model_params":
				
				* "num_predict": Il valore di fallback del parametro "num_predict" di Ollama
	"""
	
	def __init__(
			self,
	        config_dict: Dict[str, Any]
	):
		"""
			Costruisce un nuovo OllamaGeneralConfigValidator fornendogli il dizionario Python
			di configurazione che verrà associato a questo validatore
			
			Parameters
			----------
				config_dict: Dict[str, Any]
					Un dizionario variegato, indicizzato da stringhe, rappresentante il file di
					configurazione letto.
			
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il dizionario fornito ha valore `None`
						- Il dizionario fornito è vuoto
						
				InvalidConfigFilepathError
					Si verifica se:
					
						- La path del file di configurazione fornita risulta invalida sintatticamente
						- Non è possibile aprire il file di configurazione
		"""
		super().__init__(config_dict)
	
	
	def _ap__assert_platspec(
			self,
			config_read: Dict[str, Any]
	):
		num_predict: int = config_read["default_model_params"].get("num_predict", None)
		if num_predict is not None:
			if not isinstance(num_predict, int):
				raise InvalidConfigValueError()
			
			if num_predict < -2:
				raise InvalidConfigValueError()


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================