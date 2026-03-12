from ..a_ollama_specimpl import AOllamaLlmSpecImpl



class Ollama_Qwen3Coder_30b_q4_km_LlmImpl(AOllamaLlmSpecImpl):
	"""
		Rappresenta un `AOllamaLlmSpecImpl` per il modello "Qwen3-Coder-30B-q4_K_M"
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo Ollama_Qwen3Coder_30b_q4_km_LlmImpl
		"""
		super().__init__()
	
	
	def model_name(self) -> str:
		return "qwen3-coder:30b"

	
	def context_window(self) -> int:
		return 256000


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================