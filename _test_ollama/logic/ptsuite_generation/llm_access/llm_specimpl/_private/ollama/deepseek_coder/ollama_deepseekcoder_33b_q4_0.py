from ..a_ollama_specimpl import AOllamaLlmSpecImpl



class Ollama_DeepseekCoder_33b_q4_0_LlmImpl(AOllamaLlmSpecImpl):
	"""
		Rappresenta un `AOllamaLlmSpecImpl` per il modello "Deepseek-Coder-33B-q4_0"
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo Ollama_DeepseekCoder_33b_q4_0_LlmImpl
		"""
		super().__init__()
	
	
	def model_name(self) -> str:
		return "deepseek-coder:33b"
	
	
	def context_window(self) -> int:
		return 16000


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================