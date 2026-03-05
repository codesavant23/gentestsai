from abc import abstractmethod
from .. import ILlmApi



class _ABaseLlmApi(ILlmApi):
	"""
		Rappresenta un `ILlmApi` di base, ovvero che contiene
		la logica comune ad ogni `ILlmApi`
	"""
	
	
	def __hash__(self):
		return hash(self.api_name())
	
	
	def __eq__(self, __value):
		if not isinstance(__value, ILlmApi):
			return False
		
		return self.api_name() == __value.api_name()
	
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================


	@abstractmethod
	def api_name(self) -> str:
		pass
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================