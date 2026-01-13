from abc import abstractmethod
from .. import ILlmHyperParamId



class ATemperatureHyperParamId(ILlmHyperParamId):
	"""
		Rappresenta un `ILlmHyperParamId` che descrive l' iperparametro
		della temperatura.
		
		Ogni iperparametro "Temperatura" ha nome "temperature".
		
		I modelli e/o le specifiche APIs, a cui appartengono l' iperparametro specifico, sono descritti/e
		dai discendenti di questa interfaccia
	"""
	
	
	def name(self) -> str:
		return "temperature"
	
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================

	
	@abstractmethod
	def id(self) -> str:
		pass
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================