from typing import List, Set
from abc import abstractmethod
from .. import ILlmApiAccessor

from ...llm_api import ILlmApi
from ...llm_chat import ILlmChat
from ...llm_hyperparam import ILlmHyperParam
from ...llm_hyperparam.id import ILlmHyperParamId
from ...llm_specimpl import ILlmSpecImpl

from ..exceptions import (
	ChatNeverSelectedError,
	ModelNotSelectedError,
	IncompatibleApiError,
	IncompatibleHyperparamError,
	HyperparamNotExistsError,
	HyperparamAlreadyExistsError
)



class _ABaseLlmApiAccessor(ILlmApiAccessor):
	"""
		Rappresenta un `ILlmApiAccessor` di base, ovvero che contiene la logica
		di controllo comune ad ogni `ILlmApiAccessor`.
		
		La specifica API a cui è legato ogni oggetto ILlmApiAccessor è descritta dai discendenti di
		questa classe astratta.
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo _ABaseLlmApiAccessor
		"""
		self._erase_chat: bool = False
		self._model: ILlmSpecImpl = None
		self._hparams: List[ILlmHyperParam] = list()
		self._repr_api: ILlmApi = None
		self._chat: ILlmChat = None
	
	
	def set_chat(
			self,
			chat: ILlmChat,
			erase_now: bool = True,
			erase_model: bool = True
	):
		if chat is None:
			raise ValueError()
		
		if self._repr_api is None:
			self._repr_api = self._ap__accepted_api()
		if self._repr_api not in chat.compat_apis():
			raise IncompatibleApiError()
		
		self._chat = chat
		if erase_now:
			self._chat.clear()
		self._erase_chat = erase_model
	
	
	def select_model(
			self,
			model: ILlmSpecImpl
	):
		if model is None:
			raise ValueError()
		if self._chat is None:
			raise ChatNeverSelectedError()
		if self._repr_api in model.compat_apis():
			raise IncompatibleApiError()
		
		self._model = model
		self._hparams.clear()
		if self._erase_chat:
			self._chat.clear()
	
	
	def add_hyperparam(self, hparam: ILlmHyperParam):
		if hparam is None:
			raise ValueError()
		if self._chat is None:
			raise ChatNeverSelectedError()
		if self._model is None:
			raise ModelNotSelectedError()
		if self._model.model_hyperparams().intersection({hparam.param_id()}) == {}:
			raise IncompatibleHyperparamError()
		
		set_ids: Set[ILlmHyperParamId] = {hparam_c.param_id() for hparam_c in self._hparams}
		if hparam.param_id() in set_ids:
			raise HyperparamAlreadyExistsError()
		
		self._hparams.append(hparam)
	
	
	def remove_hyperparam(self, hparam: ILlmHyperParam):
		if hparam is None:
			raise ValueError()
		if self._chat is None:
			raise ChatNeverSelectedError()
		if self._model is None:
			raise ModelNotSelectedError()
		
		list_ids: List[ILlmHyperParamId] = [hparam_c.param_id() for hparam_c in self._hparams]
		if hparam.param_id() not in list_ids:
			raise HyperparamNotExistsError()
		
		to_remove: int = list_ids.index(hparam.param_id())
		self._hparams.pop(to_remove)
	
	
	def prompt(
			self,
			timeout: int
	) -> str:
		if self._chat is None:
			raise ChatNeverSelectedError()
		if self._model is None:
			raise ModelNotSelectedError()
		if timeout < 1:
			raise ValueError()
		
		response: str = self._ap__prompt_spec(
			self._chat.chat_messages(),
			self._model,
			self._hparams,
			timeout
		)
		self._chat.add_response(response)
		
		return response
	
	
	#	============================================================
	#						ABSTRACT METHODS
	#	============================================================


	@abstractmethod
	def _ap__prompt_spec(
			self,
			chat: ILlmChat,
			model: ILlmSpecImpl,
			hparams: List[ILlmHyperParam],
			timeout: int
	) -> str:
		"""
			Effettua una singola interazione, tramite l' API specifica, con il modello selezionato fornendogli
			il prompt dato come argomento.
			
			E' garantito all' interno di questo metodo:
				- Che `timeout >= 1`
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
				
			Returns
			-------
				str
					Una stringa contenente la risposta del modello all' interazione effettuata

			Raises
			------
				InvalidPromptError
					Si verifica se `user_prompt` è invalido per l' API rappresentata
					
				ApiConnectionError
					Si verifica se avviene un errore di connessione con la piattaforma di inferenza.
					L' errore è appartenente al suo dominio.
					Si utilizza l' attributo `args[0]`, di tipo stringa, per distinguere la natura dell' errore:
					
						- "timeout": La natura dell' errore riguarda il timeout di connesione
						- "other": La natura dell' errore è di altro tipo (comprensibile dalle altre componenti di `args`)
				
				ResponseTimedOutError
					Si verifica se scatta il tempo `timeout` indicato e non è stata ricevuta
					alcuna parte della risposta
					
				ApiResponseError
					Si verifica se la richiesta fornita all' API produce un errore di risposta
					appartenente al suo dominio.
					Si utilizza l' attributo `args[0]`, di tipo stringa, per distinguere la natura dell' errore:
					
						- "known": La natura dell' errore è descritta dalla piattaforma di inferenza
						- "unknown": La natura dell' errore non è descritta dalla piattaforma di inferenza ed è sconosciuta
					
				SaturatedContextWindowError
					Si verifica se viene saturata la finestra di contesto durante l' interazione
		"""
		
		
	@abstractmethod
	def _ap__accepted_api(self) -> ILlmApi:
		"""
			Restituisce l' oggetto che identifica dell' API associata a questo ILlmApiAccessor.
			
			Returns
			-------
				ILlmApi
					Un oggetto `ILlmApi` rappresentante l' identificativo dell' API
					associata a questo ILlmApiAccessor
		"""
		pass
		
		
	#	============================================================
	#						PRIVATE METHODS
	#	============================================================