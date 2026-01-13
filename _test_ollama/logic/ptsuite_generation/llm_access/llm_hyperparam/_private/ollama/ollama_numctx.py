from typing import Any
from .._a_base_llmhyperparam import _ABaseLlmHyperparam

from ....llm_hyperparam_id import (
	ILlmHyperParamId,
	OllamaNumCtxHyperParamId
)



class OllamaNumCtxHyperParam(_ABaseLlmHyperparam):
	"""
		Rappresenta un `ILlmHyperParam` per l' iperparametro "num_ctx" per ogni
		LLM con cui interagire tramite la piattaforma "Ollama".
		
		Il tipo di valori dell' iperparametro è `int`.
		E' necessario inoltre che: `valore >= 1`
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo OllamaNumCtxHyperParam
		"""
		super().__init__()
		
		
	def _ap__param_id(self) -> ILlmHyperParamId:
		return OllamaNumCtxHyperParamId()
	
	
	def _ap__default_value(self) -> str:
		return "1"
	
	
	def _ap__assert_semvalidity(
			self,
			value: str
	):
		value_int: int = int(value)
		if value_int < 1:
			raise ValueError()
		
		
	def to_effvalue(self) -> Any:
		return int(self._p__get_str_value())


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================