from typing import Set
from abc import abstractmethod
from ... import ILlmSpecImpl

from ....llm_api import (
	ILlmApi,
	OllamaApi
)
from ....llm_hyperparam.id import (
	ILlmHyperParamId,
	ILlmHyperParamIdFactory, LlmHyperParamIdFactoryResolver
)



class AOllamaLlmSpecImpl(ILlmSpecImpl):
	"""
		Rappresenta un `ILlmSpecImpl` legata all' API di "Ollama"
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo AOllamaLlmSpecImpl
		"""
		hparamid_f: ILlmHyperParamIdFactory = LlmHyperParamIdFactoryResolver.resolve("ollama")
		self._ollama_hparams: Set[ILlmHyperParamId] = {
			hparamid_f.create("temperature"),
			hparamid_f.create("top-k"),
			hparamid_f.create("top-p"),
			hparamid_f.create("gen_seed"),
			hparamid_f.create("context_window"),
			hparamid_f.create("think"),
			hparamid_f.create("num_predict"),
			hparamid_f.create("num_gpu")
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