from abc import abstractmethod
from ._a_base_hparamid import _ABaseHyperParamId



class _ASeedHyperParamId(_ABaseHyperParamId):
	"""
		Rappresenta un `ILlmHyperParamId` che descrive l' iperparametro
		del seed della generazione.
		
		Ogni iperparametro "Seed di generazione" ha nome "gen_seed".
		
		I modelli e/o le specifiche APIs, a cui appartengono l' iperparametro specifico, sono descritti/e
		dai discendenti di questa interfaccia
	"""
	
	
	def name(self) -> str:
		return "gen_seed"
	
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================

	
	@abstractmethod
	def id(self) -> str:
		pass
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================