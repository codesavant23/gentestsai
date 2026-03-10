from .._a_wantsthinking_hparamid import _AWantsThinkingHyperParamId



class OllamaThinkHyperParamId(_AWantsThinkingHyperParamId):
	"""
		Rappresenta un `AWantsThinkingHyperParamId` per ogni LLM con cui interagire
		tramite la piattaforma "Ollama".
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo OllamaThinkHyperParamId
		"""
		pass
	
	
	def id(self) -> str:
		return "think"


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================