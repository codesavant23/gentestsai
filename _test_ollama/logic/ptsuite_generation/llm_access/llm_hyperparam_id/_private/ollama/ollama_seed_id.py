from ... import ASeedHyperParamId



class OllamaSeedHyperParamId(ASeedHyperParamId):
	"""
		Rappresenta un `ASeedHyperParamId` per ogni LLM con cui interagire
		tramite la piattaforma "Ollama".
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo OllamaSeedHyperParamId
		"""
		pass
	
	
	def id(self) -> str:
		return "seed"


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================