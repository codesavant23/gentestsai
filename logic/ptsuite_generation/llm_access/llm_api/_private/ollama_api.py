from ._a_base_llmapi import _ABaseLlmApi



class OllamaApi(_ABaseLlmApi):
	"""
		Rappresenta un `ILlmApi` per identificare l' API "Ollama"
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo OllamaApi
		"""
		pass
	
	
	def api_name(self) -> str:
		return "ollama"


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================