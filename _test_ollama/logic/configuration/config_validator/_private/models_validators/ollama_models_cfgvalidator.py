from typing import Dict, Any
from ... import AModelsConfigValidator



class OllamaModelsConfigValidator(AModelsConfigValidator):
	"""
		Rappresenta un `AModelsConfigValidator` per la piattaforma di inferenza
		di nome "Ollama".
		
		I campi specifici della piattaforma sono:
		
			- In ogni entry, opzionalmente:
				
				* "num_predict": Il valore del parametro "num_predict" di Ollama per quel modello
	"""
	
	def __init__(
			self,
			config_dict: Dict[str, Any]
	):
		"""
			Costruisce un nuovo OllamaModelsConfigValidator fornendogli il dizionario Python
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
		"""
		super().__init__(config_dict)
	
	
	def _ap__assert_platspec(self, config_read: Dict[str, Any]):
		num_predict: int
		for llm_name, llm_params in config_read.items():
			num_predict = llm_params.get("num_predict", None)
			self._pf__assert_validtype("num_predict", num_predict, int, llm_name)
			

	##	============================================================
	##						PRIVATE METHODS
	##	============================================================