from typing import Any
from .._a_base_llmhyperparam import _ABaseLlmHyperparam

from ...id import ILlmHyperParamId
from ...id._private.ollama.ollama_think_id import OllamaThinkHyperParamId



class OllamaThinkHyperParam(_ABaseLlmHyperparam):
	"""
		Rappresenta un `ILlmHyperParam` per l' iperparametro "think" per ogni
		LLM con cui interagire tramite la piattaforma "Ollama".
		
		Il tipo di valori dell' iperparametro è `bool`
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo OllamaThinkHyperParam
		"""
		super().__init__()
		
		
	def _ap__param_id(self) -> ILlmHyperParamId:
		return OllamaThinkHyperParamId()
	
	
	def _ap__default_value(self) -> str:
		return "False"
	
	
	def _ap__assert_semvalidity(
			self,
			value: str
	):
		value_str: str = value.capitalize()
		if (value_str != "True") and (value_str != "False"):
			raise ValueError()
		
		
	def to_effvalue(self) -> Any:
		value_str: str = self._p__get_str_value().capitalize()
		if value_str != "True":
			value_str = ""
		return bool(value_str)


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================