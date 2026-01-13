from abc import abstractmethod
from .. import ILlmHyperParamId



class AWantsThinkingHyperParamId(ILlmHyperParamId):
	"""
		Rappresenta un `ILlmHyperParamId` che descrive l' iperparametro
		"è richiesto l' utilizzo del thinking".
		
		Ogni iperparametro "Thinking richiesto" ha nome "think".
		
		I modelli e/o le specifiche APIs, a cui appartengono l' iperparametro specifico, sono descritti/e
		dai discendenti di questa interfaccia
	"""
	
	
	def name(self) -> str:
		return "think"
	
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================

	
	@abstractmethod
	def id(self) -> str:
		pass
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================