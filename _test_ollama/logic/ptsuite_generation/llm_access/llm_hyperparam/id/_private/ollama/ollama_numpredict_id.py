from ... import ILlmHyperParamId



class OllamaNumPredictHyperParamId(ILlmHyperParamId):
	"""
		Rappresenta un `ILlmHyperParamId` per l' iperparametro "num_predict" per ogni
		LLM con cui interagire tramite la piattaforma "Ollama".
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo OllamaNumPredictHyperParam
		"""
		pass
	
	
	def name(self) -> str:
		return "num_predict"
	
	
	def id(self) -> str:
		return "num_predict"


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================