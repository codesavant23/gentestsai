from .._a_contextwin_hparamid import _AContextWindowHyperParamId



class OllamaNumCtxHyperParamId(_AContextWindowHyperParamId):
	"""
		Rappresenta un `AContextWindowHyperParamId` per ogni LLM con cui interagire
		tramite la piattaforma "Ollama".
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo OllamaNumCtxHyperParamId
		"""
		pass
		
		
	def id(self) -> str:
		return "num_ctx"


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================