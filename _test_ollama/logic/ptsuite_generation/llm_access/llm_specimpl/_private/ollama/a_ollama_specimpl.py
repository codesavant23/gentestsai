from typing import Set
from abc import abstractmethod
from ... import ILlmSpecImpl

from ....llm_api import (
	ILlmApi,
	OllamaApi
)
from ....llm_hyperparam_id import (
	ILlmHyperParamId,
	OllamaTemperatureHyperParamId,
	OllamaNumPredictHyperParamId,
	OllamaTopKHyperParamId,
	OllamaTopPHyperParamId,
	OllamaSeedHyperParamId,
	OllamaNumCtxHyperParamId,
	OllamaThinkHyperParamId
)



class AOllamaLlmSpecImpl(ILlmSpecImpl):
	"""
		Rappresenta un `ILlmSpecImpl` legata all' API di "Ollama"
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo AOllamaLlmSpecImpl
		"""
		self._ollama_hparams: Set[ILlmHyperParamId] = {
			OllamaTemperatureHyperParamId(),
			OllamaNumPredictHyperParamId(),
			OllamaTopKHyperParamId(),
			OllamaTopPHyperParamId(),
			OllamaSeedHyperParamId(),
			OllamaNumCtxHyperParamId(),
			OllamaThinkHyperParamId()
		}
		self._compat_apis: Set[ILlmApi] = {OllamaApi()}
	
	
	def model_hyperparams(self) -> Set[ILlmHyperParamId]:
		return self._ollama_hparams
	
	
	def compat_apis(self) -> Set[ILlmApi]:
		return self._compat_apis
	
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	
	
	@abstractmethod
	def model_name(self) -> str:
		pass
	
	
	@abstractmethod
	def context_window(self) -> int:
		pass
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================