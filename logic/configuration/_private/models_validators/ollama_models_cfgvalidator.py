from typing import Dict, Any
from .a_models_cfgvalidator import AModelsConfigValidator



class OllamaModelsConfigValidator(AModelsConfigValidator):
	"""
		Represents an `AModelsConfigValidator` for the inference platform
        named "Ollama".
		
		The platform-specific fields are:
        
            - In each entry, optionally:
                
                * "num_predict": The value of Ollama's "num_predict" parameter for that model
	"""
	
	def __init__(
			self,
			config_dict: Dict[str, Any]
	):
		"""
			Creates a new OllamaModelsConfigValidator by providing it with the Python configuration dictionary
            that will be associated with this validator
            
            Parameters
            ----------
				config_dict: Dict[str, Any]
                    A mixed dictionary, indexed by strings, representing the read configuration file.
			
			Raises
            ------
                ValueError
                    Occurs if:
                    
                        - The provided dictionary has a value of `None`
                        - The provided dictionary is empty
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