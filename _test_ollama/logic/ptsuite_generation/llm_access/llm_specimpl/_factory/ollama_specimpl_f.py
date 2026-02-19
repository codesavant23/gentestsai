from .. import ILlmSpecImplFactory

from .. import ILlmSpecImpl
from .....variability import ESpecLlmImpl
from .._private.ollama.qwen3.ollama_qwen3_32b_q4_km import Ollama_Qwen3_32b_q4_km_LlmImpl
from .._private.ollama.deepseek_coder.ollama_deepseekcoder_33b_q4_0 import Ollama_DeepseekCoder_33b_q4_0_LlmImpl



class OllamaSpecImplFactory(ILlmSpecImplFactory):
	"""
		Rappresenta una factory per ogni `ILlmSpecImpl` relativo alla piattaforma
		di inferenza Ollama
	"""
	
	
	def create(self, model: ESpecLlmImpl) -> ILlmSpecImpl:
		match model:
			case ESpecLlmImpl.QWEN3_32B_Q4_K_M:
				return Ollama_Qwen3_32b_q4_km_LlmImpl()
			case ESpecLlmImpl.DEEPSEEK_CODER_33B_Q4_0:
				return Ollama_DeepseekCoder_33b_q4_0_LlmImpl()
			case _:
				raise NotImplementedError()


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================