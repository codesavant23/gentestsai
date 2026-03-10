from typing import Any
from .._a_base_llmhyperparam import _ABaseLlmHyperparam

from ...id import ILlmHyperParamId
from ...id._private.ollama.ollama_numgpu_id import OllamaNumGpuHyperParamId



class OllamaNumGpuHyperParam(_ABaseLlmHyperparam):
	"""
		Rappresenta un `ILlmHyperParam` per l' iperparametro "num_gpu" per ogni
		LLM con cui interagire tramite la piattaforma "Ollama".
		
		Il tipo di valori dell' iperparametro è `int`.
		E' necessario inoltre che: `valore >= 0`.
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo OllamaNumGpuHyperParam
		"""
		super().__init__()
	
	
	def _ap__param_id(self) -> ILlmHyperParamId:
		return OllamaNumGpuHyperParamId()
	
	
	def _ap__default_value(self) -> str:
		return "0"
	
	
	def _ap__assert_semvalidity(self, value: str):
		value_int: int = int(value)
		if value_int < 0:
			raise ValueError()
		
		
	def to_effvalue(self) -> Any:
		return int(self._p__get_str_value())


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================