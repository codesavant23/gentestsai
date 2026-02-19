from .._a_temperature_hparamid import _ATemperatureHyperParamId



class OllamaTemperatureHyperParamId(_ATemperatureHyperParamId):
	"""
		Rappresenta un `ATemperatureHyperParamId` per ogni LLM con cui interagire
		tramite la piattaforma "Ollama".
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo OllamaTemperatureHyperParamId
		"""
		pass
	
	
	def id(self) -> str:
		return "temperature"


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================