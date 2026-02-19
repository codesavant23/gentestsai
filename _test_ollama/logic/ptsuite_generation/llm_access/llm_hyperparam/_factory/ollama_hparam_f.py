from .. import ILlmHyperParamFactory

from .. import ILlmHyperParam
from .._private.ollama.ollama_temperature import OllamaTemperatureHyperParam
from .._private.ollama.ollama_numctx import OllamaNumCtxHyperParam
from .._private.ollama.ollama_seed import OllamaSeedHyperParam
from .._private.ollama.ollama_topp import OllamaTopPHyperParam
from .._private.ollama.ollama_topk import OllamaTopKHyperParam
from .._private.ollama.ollama_think import OllamaThinkHyperParam
from .._private.ollama.ollama_numpredict import OllamaNumPredictHyperParam
from .._private.ollama.ollama_numgpu import OllamaNumGpuHyperParam



class OllamaHyperParamFactory(ILlmHyperParamFactory):
	"""
		Rappresenta una factory per ogni `ILlmHyperParam` relativo alla piattaforma
		di inferenza Ollama
	"""
	
	
	def create(self, param_id: str) -> ILlmHyperParam:
		match param_id:
			case "temperature":
				return OllamaTemperatureHyperParam()
			case "context_window":
				return OllamaNumCtxHyperParam()
			case "top-k":
				return OllamaTopKHyperParam()
			case "top-p":
				return OllamaTopPHyperParam()
			case "think":
				return OllamaThinkHyperParam()
			case "gen_seed":
				return OllamaSeedHyperParam()
			case "num_predict":
				return OllamaNumPredictHyperParam()
			case "num_gpu":
				return OllamaNumGpuHyperParam()
			case _:
				raise NotImplementedError()


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================