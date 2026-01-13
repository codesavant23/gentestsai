from typing import Any
from .._a_base_llmhyperparam import _ABaseLlmHyperparam

from ....llm_hyperparam_id import (
	ILlmHyperParamId,
	OllamaTemperatureHyperParamId
)



class OllamaTemperatureHyperParam(_ABaseLlmHyperparam):
	"""
		Rappresenta un `ILlmHyperParam` per l' iperparametro "temperatura" per ogni
		LLM con cui interagire tramite la piattaforma "Ollama".
		
		Il tipo di valori dell' iperparametro è `float`.
		E' necessario inoltre che: `0.0 <= valore <= 1.0`
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo OllamaTemperatureHyperParam
		"""
		super().__init__()
	
	
	def _ap__param_id(self) -> ILlmHyperParamId:
		return OllamaTemperatureHyperParamId()
	
	
	def _ap__default_value(self) -> str:
		return "0.5"
	
	
	def _ap__assert_semvalidity(self, value: str):
		temp: float = float(value)
		if (temp < 0.0) or (temp > 1.0):
			raise ValueError()
	
	
	def to_effvalue(self) -> Any:
		return float(self._p__get_str_value())


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================