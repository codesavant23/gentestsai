from abc import abstractmethod
from .. import ILlmHyperParamId



class AContextWindowHyperParamId(ILlmHyperParamId):
	"""
		Rappresenta un `ILlmHyperParamId` che descrive l' iperparametro
		della finestra di contesto.
		
		Ogni iperparametro "Finestra di contesto" ha nome "context_name".
		
		I modelli e/o le specifiche APIs, a cui appartengono l' iperparametro specifico, sono descritti/e
		dai discendenti di questa interfaccia
	"""
	
	
	def name(self) -> str:
		return "context_window"
	
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================

	
	@abstractmethod
	def id(self) -> str:
		pass
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================