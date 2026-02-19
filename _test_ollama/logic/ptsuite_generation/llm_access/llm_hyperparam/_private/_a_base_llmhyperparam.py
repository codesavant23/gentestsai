from abc import abstractmethod
from .. import ILlmHyperParam

from ..id import ILlmHyperParamId



class _ABaseLlmHyperparam(ILlmHyperParam):
	"""
		Rappresenta un `ILlmHyperParam` di base, ovvero che contiene la logica
		di controllo comune ad ogni `ILlmHyperParam`
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo _ABaseLlmHyperparam
		"""
		self._id: ILlmHyperParamId = self._ap__param_id()
		self._value: str = self._ap__default_value()
	
	
	def param_id(self) -> ILlmHyperParamId:
		return self._id
	
	
	def set_value(self, value: str):
		if (value is None) or (value == ""):
			raise ValueError()
		
		self._ap__assert_semvalidity(value)
		
		self._value = value
		
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	
	
	@abstractmethod
	def _ap__param_id(self) -> ILlmHyperParamId:
		"""
			Restituisce l' identificatore dell' iperparametro associato all'
			iperparametro rappresentato
			
			Returns
			-------
				ILlmHyperParamId
					Un oggetto `ILlmHyperParamId` rappresentante l' identificatore associato
					a questo iperparametro
		"""
		pass
	
	
	@abstractmethod
	def _ap__default_value(self) -> str:
		"""
			Restituisce il valore di default per l' iperparametro rappresentato
			
			Returns
			-------
				str
					Una stringa rappresentante il valore di default per l' iperparametro
					rappresentato.
					Il valore di default non deve essere obbligatoriamente valido
					per l' iperparametro. Può anche essere un inizializzazione invalida
					per la sua semantica
		"""
		pass
	
	
	@abstractmethod
	def _ap__assert_semvalidity(self, value: str):
		"""
			Verifica la validità semantica del valore fornito per l' iperparametro
			rappresentato.
			
			Se la verifica ha successo quest' operazione è equivalente ad una no-op
			
			Parameters
			----------
				value: str
					Una stringa rappresentante il valore dell' iperparametro da verificare
					
			Raises
			------
				ValueError
					Si verifica se il parametro value contiene un valore invalido per
					l' iperparametro rappresentato
				
		"""
		pass
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	def _p__get_str_value(self) -> str:
		"""
			Restituisce il valore, come stringa, attualmente assegnato all'
			iperparametro rappresentato
			
			Returns
			-------
				str
					Una stringa rappresentante il valore attualmente assegnato all'
					iperparametro rappresentato
		"""
		return self._value