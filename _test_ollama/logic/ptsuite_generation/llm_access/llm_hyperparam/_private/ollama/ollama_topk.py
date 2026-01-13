from typing import Any
from .._a_base_llmhyperparam import _ABaseLlmHyperparam

from ....llm_hyperparam_id import (
	ILlmHyperParamId,
	OllamaTopKHyperParamId
)



class OllamaTopKHyperParam(_ABaseLlmHyperparam):
	"""
		Rappresenta un `ILlmHyperParam` per l' iperparametro "top-k" per ogni
		LLM con cui interagire tramite la piattaforma "Ollama".
		
		Il tipo di valori dell' iperparametro è `int`.
		E' necessario inoltre che: `valore >= 0`
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo OllamaTopKHyperParam
		"""
		super().__init__()
	
	
	def _ap__param_id(self) -> ILlmHyperParamId:
		return OllamaTopKHyperParamId()
	
	
	def _ap__default_value(self) -> str:
		return "40"
	
	
	def _ap__assert_semvalidity(self, value: str):
		topk: int = int(value)
		if topk < 0:
			raise ValueError()
	
	
	def to_effvalue(self) -> Any:
		return int(self._p__get_str_value())


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================