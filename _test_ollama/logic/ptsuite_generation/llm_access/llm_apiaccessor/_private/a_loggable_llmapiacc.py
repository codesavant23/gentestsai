from typing import List
from abc import abstractmethod
from ._a_base_llmapiacc import _ABaseLlmApiAccessor

from .....utils.logger import ATemporalFormattableLogger
from ...llm_api import ILlmApi
from ...llm_chat import ILlmChat
from ...llm_hyperparam import ILlmHyperParam
from ...llm_specimpl import ILlmSpecImpl



class ALoggableLlmApiAccessor(_ABaseLlmApiAccessor):
	"""
		Rappresenta un `ILlmApiAccessor` che permette di loggare dei passaggi effettuati
		durante la richiesta di prompting.
		
		La specifica API a cui è legato ogni oggetto ILlmApiAccessor è descritta dai discendenti
		di questa classe astratta.
		I passaggi che vengono loggati sono specificati dai discendenti di questa classe astratta.
	"""
	
	def __init__(
			self,
			chat: ILlmChat,
			logger: ATemporalFormattableLogger=None,
			logger_sep: str="\n"
	):
		"""
			Costruisce un nuovo ALoggableLlmApiAccessor associandolo, opzionalmente,
			al logger che verrà utilizzato per registrare i passaggi
			
			Parameters
			----------
				logger: ATemporalFormattableLogger
					Opzionale. Default = `None`. Un oggetto `ATemporalFormattableLogger` rappresentante il logger
					da utilizzare per registrare i passaggi effettuati da questo `ILlmApiAccessor`
					durante ogni richiesta effettuata
					
				logger_sep: str
					Opzionale. Default = `\\n`. Una stringa contenente il separatore da utilizzare per i
					messaggi di logging che verranno registrati.
					
			Raises
			------
				ValueError
					Si verifica se il parametro `chat` ha valore `None`
		"""
		super().__init__(chat)
		
		self._logger: ATemporalFormattableLogger = logger
		self._logger_sep: str = None
		if logger is not None:
			self._logger_sep = logger_sep if logger_sep is not None else "\n"
	
	
	def _ap__prompt_spec(
			self,
			chat: ILlmChat,
			model: ILlmSpecImpl,
			hparams: List[ILlmHyperParam],
			timeout: int
	) -> str:
		return self._ap__prompt_withlog(
			chat, model, hparams, timeout,
			logger=self._logger
		)
	

	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	
	
	@abstractmethod
	def _ap__accepted_api(self) -> ILlmApi:
		pass
	
	
	@abstractmethod
	def _ap__prompt_withlog(
			self,
			chat: ILlmChat,
			model: ILlmSpecImpl,
			hparams: List[ILlmHyperParam],
			timeout: int,
			logger: ATemporalFormattableLogger=None
	) -> str:
		"""
			Effettua una singola interazione, tramite l' API specifica, con il modello selezionato fornendogli
			il prompt dato come argomento e, opzionalmente, loggando i passaggi specificati dai discendenti
			di questa classe astratta.
			
			Se per il `logger` non è impostata una stringa di formato, i discendenti di questa classe astratta
			ne forniscono una di default.
			
			E' garantito all' interno di questo metodo:
				- Che il parametro `user_prompt` non sia `None` nè una stringa vuota
				- Che il modello `model` sia accettato dall' API
				- Che ogni iperparametro di `hparams` è valido per il modello `model`

			Parameters
			----------
				chat: ILlmChat
					Un oggetto `ILlmChat` rappresentante la chat da utilizzare per effettuare
					l' interazione con il modello
					
				model: ILlmSpecImpl
					Un oggetto `ILlmSpecImpl` rappresentante il LLM con cui effettuare l'interazione
					
				hparams: List[ILlmHyperParam]
					Un oggetto `ILlmHyperParam` rappresentante l' elenco di iperparametri da utilizzare
					in questa interazione
					
				timeout: int
					Un intero rappresentante il timeout in millisecondi dopo il quale
					dichiarare la risposta fallita
					
				logger: ATemporalFormattableLogger
					Opzionale. Default = `None`. Un oggetto `ATemporalFormattableLogger` rappresentante il logger da utilizzare
					per registrare i passaggi effettuati da questo `ILlmApiAccessor` durante
					ogni richiesta effettuata
				
			Returns
			-------
				str
					Una stringa contenente la risposta del modello all' interazione effettuata

			Raises
			------
				InvalidPromptError
					Si verifica se `user_prompt` è invalido per l' API rappresentata
					
				ApiResponseError
					Si verifica se la richiesta fornita all' API produce un errore sconosciuto
					ma appartenente al suo dominio
					
				SaturatedContextWindowError
					Si verifica se viene saturata la finestra di contesto durante l' interazione
		"""
		pass
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================