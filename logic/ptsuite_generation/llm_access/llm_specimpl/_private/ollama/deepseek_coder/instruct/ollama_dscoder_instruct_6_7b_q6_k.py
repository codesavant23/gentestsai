from ...a_ollama_specimpl import AOllamaLlmSpecImpl



class Ollama_DeepseekCoder_6_7b_instruct_q6_k_LlmImpl(AOllamaLlmSpecImpl):
	"""
		Rappresenta un `AOllamaLlmSpecImpl` per il modello "Deepseek-Coder-6.7b-instruct-q6_K"
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo Ollama_DeepseekCoder_6_7b_instruct_q6_k_LlmImpl
		"""
		super().__init__()
	
	
	def model_name(self) -> str:
		return "deepseek-coder:6.7b-instruct-q6_K"
	
	
	def context_window(self) -> int:
		return 16384


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================