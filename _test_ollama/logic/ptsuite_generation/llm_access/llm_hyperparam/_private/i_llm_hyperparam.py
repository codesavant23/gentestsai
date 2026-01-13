from typing import Any
from abc import ABC, abstractmethod

from ...llm_hyperparam_id import ILlmHyperParamId



class ILlmHyperParam(ABC):
	"""
		Rappresenta un iperparametro specifico di uno, o più, LLMs.

		Ogni iperparametro specifico è legato ad un solo identificatore di iperparametro.

		Il parametro specifico e la sua semantica rappresentati, sono descritti dall' identificatore scelto
		e resi noti all' utilizzatore dai discendenti di questa interfaccia.
		I modelli e/o le specifiche APIs, a cui appartengono il parametro specifico, sono descritti/e
		dall' identificatore scelto e resi noti all' utilizzatore dai discendenti di questa interfaccia
	"""


	@abstractmethod
	def param_id(self) -> ILlmHyperParamId:
		"""
			Restituisce l' identificatore dell' iperparametro rappresentato

			Returns
			-------
				ILlmHyperParamId
					Un oggetto `ILlmHyperParamId` rappresentante l' identificatore
					dell' iperparametro che rappresenta
		"""
		pass


	@abstractmethod
	def set_value(self, value: str):
		"""
			Imposta il valore dato come argomento come valore per l' iperparametro LLM-specifico
			rappresentato da questo ILlmHyperParam.

			Parameters
			----------
				value: str
					Una stringa contenente il valore da impostare per questo ILlmHyperParam

			Raises
			------
				ValueError
					Si verifica se:
					
						- Il parametro `value` ha valore `None`
						- Il parametro `value` è una stringa vuota
						- Il parametro `value` contiene un valore invalido per l' iperparametro
						  rappresentato
		"""
		pass
	
	
	@abstractmethod
	def to_effvalue(self) -> Any:
		"""
			Restituisce il valore di questo iperparametro LLM-specifico nel tipo effettivo
			utilizzato dall' API
			
			Returns
			-------
				Any
					Un variegato rappresentante l' ultimo valore impostato per questo iperparametro
					nel tipo accettato dalle API specifiche a cui è legato questo ILlmHyperParam
		"""
		