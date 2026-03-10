from .._a_topk_hparamid import _ATopKHyperParamId



class OllamaTopKHyperParamId(_ATopKHyperParamId):
	"""
		Rappresenta un `ATopKHyperParamId` per ogni LLM con cui interagire
		tramite la piattaforma "Ollama".
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo OllamaTopKHyperParamId
		"""
		pass
	
	
	def id(self) -> str:
		return "top_k"


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================