from .._a_seed_hparamid import _ASeedHyperParamId



class OllamaSeedHyperParamId(_ASeedHyperParamId):
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