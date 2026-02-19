from abc import abstractmethod
from ._a_base_hparamid import _ABaseHyperParamId



class _ATopKHyperParamId(_ABaseHyperParamId):
	"""
		Rappresenta un `ILlmHyperParamId` che descrive l' iperparametro
		top-k.
		
		Ogni iperparametro "Top-K" ha nome "top-k".
		
		I modelli e/o le specifiche APIs, a cui appartengono l' iperparametro specifico, sono descritti/e
		dai discendenti di questa interfaccia
	"""
	
	
	def name(self) -> str:
		return "top-k"
	
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================

	
	@abstractmethod
	def id(self) -> str:
		pass
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================