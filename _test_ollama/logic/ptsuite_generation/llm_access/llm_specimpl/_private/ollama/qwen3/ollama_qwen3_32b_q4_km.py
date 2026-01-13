from .. import AOllamaLlmSpecImpl



class Ollama_Qwen3_32b_q4_km_LlmImpl(AOllamaLlmSpecImpl):
	"""
		Rappresenta un `AOllamaLlmSpecImpl` per il modello "Qwen3-32B-q4_K_M"
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo Ollama_Qwen3_32b_q4_km_LlmImpl
		"""
		super().__init__()
	
	
	def model_name(self) -> str:
		return "qwen3:32b"

	
	def context_window(self) -> int:
		return 40000


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================