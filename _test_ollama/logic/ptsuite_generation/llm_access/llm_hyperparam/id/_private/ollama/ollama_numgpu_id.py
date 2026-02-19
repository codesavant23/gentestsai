from ... import ILlmHyperParamId



class OllamaNumGpuHyperParamId(ILlmHyperParamId):
	"""
		Rappresenta un `ILlmHyperParamId` per l' iperparametro "num_gpu" per ogni
		LLM con cui interagire tramite la piattaforma "Ollama".
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo OllamaNumGpuHyperParamId
		"""
		pass
	
	
	def name(self) -> str:
		return "num_gpu"
	
	
	def id(self) -> str:
		return "num_gpu"


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================