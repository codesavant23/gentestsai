from typing import Any
from .._a_base_llmhyperparam import _ABaseLlmHyperparam

from ....llm_hyperparam_id import (
	ILlmHyperParamId,
	OllamaSeedHyperParamId
)



class OllamaSeedHyperParam(_ABaseLlmHyperparam):
	"""
		Rappresenta un `ILlmHyperParam` per l' iperparametro "seed" per ogni
		LLM con cui interagire tramite la piattaforma "Ollama".
		
		Il tipo di valori dell' iperparametro è `int`.
		E' necessario inoltre che: `valore >= -1`.
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo OllamaSeedHyperParam
		"""
		super().__init__()
	
	
	def _ap__param_id(self) -> ILlmHyperParamId:
		return OllamaSeedHyperParamId()
	
	
	def _ap__default_value(self) -> str:
		return "-1"
	
	
	def _ap__assert_semvalidity(self, value: str):
		seed :int = int(value)
		if seed < -1:
			raise ValueError()
	
	
	def to_effvalue(self) -> Any:
		return int(self._p__get_str_value())


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================