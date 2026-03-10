from typing import Set
from abc import ABC, abstractmethod

from ...llm_api import ILlmApi
from ...llm_hyperparam.id import ILlmHyperParamId



class ILlmSpecImpl(ABC):
	"""
		Rappresenta una specifica implementazione di un LLM, con eventuali iperparametri specifici definiti,
		legata a una o più specifiche API che ne permettono l'interazione.
		
		Ogni ILlmSpecImpl è immutabile.

		Ogni specifica caratteristica dell' implementazione è descritta dai discendenti di questa interfaccia.
		Le specifiche API, alle quali è legata l' implementazione specifica, sono descritte dai discendenti
		di questa interfaccia. Nel caso di più API esse devono coincidere in ogni specifica caratteristica
		dell' implementazione del modello per rendere questo ILlmSpecImpl valido per tutte le API associate.
	"""


	@abstractmethod
	def model_name(self) -> str:
		"""
			Restituisce il nome del modello, composto anche dalla specifica variante, che è legato
			alla specifica implementazione rappresentata.
			Il nome del modello restituito è conforme al formato delle API specifiche descritte
			dai discendenti di questa interfaccia.
			
			Returns
			-------
				str
					Una stringa, single-line, contenente il nome del modello della specifica
					implementazione rappresentata da questo ILlmSpecImpl.
					Esso è l' identificatore del modello che viene usato dalle specifiche API
		"""
		pass


	@abstractmethod
	def model_hyperparams(self) -> Set[ILlmHyperParamId]:
		"""
			Restituisce i parametri specifici, del modello, utilizzabili con questa
			specifica implementazione rappresentata.

			Returns
			-------
				Set[ILlmHyperParamId]
					Un set di oggetti `ILlmSpecParamId` rappresentante l' elenco degli iperparametri
					utilizzabili in questa specifica implementazione del LLM
		"""
		pass


	@abstractmethod
	def context_window(self) -> int:
		"""
			Restituisce la massima finestra di contesto (numero di tokens massimi fornibili),
			durante l'interazione, con il modello descritto in questa specifica implementazione.
			
			Il numero di tokens è legato alla modalità di interazione con il modello:
				- Se l' interazione è di tipo "single-prompt" allora il numero di tokens è relativo ad ogni singola interazione con il modello
				- Se l' interazione è di tipo "chat" allora il numero di tokens è relativo all' intera chat con il modello

			Returns
			-------
				int
					Un intero indicante il numero di tokens massimi fornibili durante l'interazione
					con il modello descritto da questa specifica implementazione
		"""
		pass
	
	
	@abstractmethod
	def compat_apis(self) -> Set[ILlmApi]:
		"""
			Restituisce l' insieme delle APIs di LLMs che sono compatibili con questo ILlmSpecImpl
			
			Returns
			-------
				Set[ILlmApi]
					Un insieme di oggetti `ILlmApi` rappresentante l' insieme degli identificatori
					di APIs con cui è compatibile questa specifica implementazione di un LLM
		"""
		pass