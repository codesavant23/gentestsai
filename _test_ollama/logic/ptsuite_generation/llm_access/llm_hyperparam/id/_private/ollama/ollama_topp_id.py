from .._a_topp_hparamid import _ATopPHyperParamId



class OllamaTopPHyperParamId(_ATopPHyperParamId):
	"""
		Rappresenta un `ILlmHyperParamId` per ogni LLM con cui interagire
		tramite la piattaforma "Ollama".
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo OllamaTopPHyperParamId
		"""
		pass
	
	
	def id(self) -> str:
		return "top_p"


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================