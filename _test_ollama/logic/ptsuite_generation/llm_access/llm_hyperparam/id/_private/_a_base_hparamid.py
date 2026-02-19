from abc import abstractmethod
from .. import ILlmHyperParamId



class _ABaseHyperParamId(ILlmHyperParamId):
	"""
		Rappresenta un `ILlmHyperParamId` di base, ovvero che contiene la logica
		comune ad ogni `ILlmHyperParamId`
		
		L' iperparametro e la sua semantica rappresentati sono descritti dai discendenti
		di questa classe astratta.
		I modelli e/o le specifiche APIs, a cui appartengono l' iperparametro, sono descritti/e
		dai discendenti di questa classe astratta.
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo _ABaseHyperParamId
		"""
		pass
	
	
	def __hash__(self):
		return super().__hash__()
		
		
	def __eq__(self, other):
		if not isinstance(other, ILlmHyperParamId):
			raise NotImplementedError()
		
		return self.id() == other.id()
	

	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	
	
	@abstractmethod
	def name(self) -> str:
		pass
	
	
	@abstractmethod
	def id(self) -> str:
		pass
		
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================