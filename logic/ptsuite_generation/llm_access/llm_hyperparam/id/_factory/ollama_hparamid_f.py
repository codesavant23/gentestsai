from .. import ILlmHyperParamIdFactory

from .. import ILlmHyperParamId
from .._private.ollama.ollama_temperature_id import OllamaTemperatureHyperParamId
from .._private.ollama.ollama_numctx_id import OllamaNumCtxHyperParamId
from .._private.ollama.ollama_seed_id import OllamaSeedHyperParamId
from .._private.ollama.ollama_topp_id import OllamaTopPHyperParamId
from .._private.ollama.ollama_topk_id import OllamaTopKHyperParamId
from .._private.ollama.ollama_think_id import OllamaThinkHyperParamId
from .._private.ollama.ollama_numpredict_id import OllamaNumPredictHyperParamId
from .._private.ollama.ollama_numgpu_id import OllamaNumGpuHyperParamId



class OllamaHyperParamIdFactory(ILlmHyperParamIdFactory):
	"""
		Rappresenta una factory per ogni `ILlmHyperParam` relativo alla piattaforma
		di inferenza Ollama
	"""
	
	
	def create(self, param_id: str) -> ILlmHyperParamId:
		match param_id:
			case "temperature":
				return OllamaTemperatureHyperParamId()
			case "context_window":
				return OllamaNumCtxHyperParamId()
			case "top-k":
				return OllamaTopKHyperParamId()
			case "top-p":
				return OllamaTopPHyperParamId()
			case "think":
				return OllamaThinkHyperParamId()
			case "gen_seed":
				return OllamaSeedHyperParamId()
			case "num_predict":
				return OllamaNumPredictHyperParamId()
			case "num_gpu":
				return OllamaNumGpuHyperParamId()
			case _:
				raise NotImplementedError()


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================