from abc import ABC, abstractmethod

from ...llm_chat import ILlmChat
from ...llm_specimpl import ILlmSpecImpl
from ...llm_hyperparam import ILlmHyperParam



class ILlmApiAccessor(ABC):
	"""
		Rappresenta un oggetto che permette, tramite l' utilizzo di una qualsiasi API che fornisce LLMs,
		l' interazione con un LLM.

		E' necessario, dopo la creazione di un ILlmApiAccessor, eseguire:
		
			- L' operazione `.init_accsor(...)` per l' associazione con la prima chat da utilizzare per le richieste
			- L' operazione `.select_model(...)` per la selezione del primo modello con cui avverranno le interazioni

		La specifica API a cui è legato ogni oggetto ILlmApiAccessor è descritta dai discendenti di questa interfaccia.
	"""
	
	
	@abstractmethod
	def init_accsor(self, chat: ILlmChat):
		"""
			Inizializza questo ILlmApiAccessor associandolo alla prima chat da utilizzare
			per effettuare le richieste
			
			Parameters
			----------
				chat: ILlmChat
					Un oggetto `ILlmChat` rappresentante la chat da utilizzare per
					le successive interazioni con il prossimo modello scelto.
					L' oggetto `ILlmChat` viene completamente gestito da questo `ILlmApiAccessor`
					azzerandolo ad ogni nuovo modello scelto.
					Alla fine di questa operazione la chat sarà già stata azzerata
					
			Raises
			------
				ValueError
					Si verifica se `chat` ha valore `None`
					
				IncompatibleApiError
					Si verifica se l' API rappresentata da questo oggetto è incompatibile
					con le APIs di `chat`
		"""
		pass
		

	@abstractmethod
	def set_chat(self, chat: ILlmChat, erase: bool=True):
		"""
			Cambia la chat utilizzata per le prossime interazioni tramite questo
			ILlmApiAccessor. Opzionalmente si può scegliere di non cancellare la chat
			associata.
			
			Parameters
			----------
				chat: ILlmChat
					Un oggetto `ILlmChat` rappresentante la nuova chat da associare per le
					prossime interazioni
					
				erase: bool
					Opzionale. Default = `True`. Un booleano che indica se cancellare tutti i messaggi
					dalla nuova chat associata
					
			Raises
			------
				AccessorNotInitedError
					Si verifica se questo ILlmApiAccessor non è stato inizializzato
			
				ValueError
					Si verifica se il parametro `chat` ha valore `None`
					
				IncompatibleApiError
					Si verifica se nessuna API della chat fornita è compatibile
					con l' API rappresentata
		"""
		pass


	@abstractmethod
	def select_model(self, model: ILlmSpecImpl):
		"""
			Seleziona un nuovo modello con cui questo ILlmApiAccessor effettuerà tutte le prossime
			interazioni.
			
			Se era già stato scelto un modello e impostati degli iperparametri, essi vengono rimossi

			Parameters
			----------
				model: ILlmSpecImpl
					Un ILlmSpecImpl rappresentante l' implementazione specifica, del LLM, da utilizzare
					per le successive interazioni
					La modalità di interazione dell' implementazione specifica deve coincidere
					con quella rappresentata dall' ILlmApiAccessor in utilizzo

			Raises
			------
				AccessorNotInitedError
					Si verifica se questo ILlmApiAccessor non è stato inizializzato
			
				ValueError
					Si verifica se `model` ha valore None
					
				IncompatibleApiError
					Si verifica se l' API rappresentata da questo ILlmApiAccessor non è compatibile
					con le APIs del modello scelto
		"""
		pass


	@abstractmethod
	def add_hyperparam(self, hparam: ILlmHyperParam):
		"""
			Aggiunge un nuovo iperparametro da utilizzare nelle successive interazioni

			Parameters
			----------
				hparam: ILlmHyperParam
					Un oggetto `ILlmHyperParam` rappresentante il parametro LLM-specifico di cui
					impostare il valore

			Raises
			------
				AccessorNotInitedError
					Si verifica se questo ILlmApiAccessor non è stato inizializzato
			
				ModelNotSelectedError
					Si verifica se non è stato selezionato nessun modello per questo ILlmApiAccessor
			
				ValueError
					Si verifica se il parametro `hparam` ha valore `None`
						
				IncompatibleHyperparamError
					Si verifica se l' iperparametro `hparam` fornito non è accettabile
					dalla specifica implementazione di LLM scelta
					
				HyperparamAlreadyExistsError
					Si verifica se l' iperparametro `hparam` fornito è stato già
					aggiunto a questo ILlmApiAccessor
		"""
		pass
	
	
	@abstractmethod
	def remove_hyperparam(self, hparam: ILlmHyperParam):
		"""
			Rimuove un iperparametro, precedentemente aggiunto, per le successive interazioni

			Parameters
			----------
				hparam: ILlmHyperParam
					Un oggetto `ILlmHyperParam` rappresentante l' iperparametro da rimuovere

			Raises
			------
				AccessorNotInitedError
					Si verifica se questo ILlmApiAccessor non è stato inizializzato
			
				ModelNotSelectedError
					Si verifica se non è stato selezionato nessun modello per questo ILlmApiAccessor
			
				ValueError
					Si verifica se il parametro `hparam` ha valore `None`
					
				HyperparamNotExistsError
					Si verifica se l' iperparametro `hparam` fornito non è presente tra gli
					iperparametri aggiunti a questo ILlmApiAccessor
		"""
		pass


	@abstractmethod
	def prompt(self, user_prompt: str, timeout: int) -> str:
		"""
			Effettua una singola interazione con il modello selezionato fornendogli il
			prompt dato come argomento

			Parameters
			----------
				user_prompt: str
					Una stringa, single-line o multi-line, contenente il prompt da fornire
					al modello selezionato per effettuare l' interazione
					
				timeout: int
					Un intero rappresentante il timeout in millisecondi dopo il quale
					dichiarare la risposta fallita

			Returns
			-------
				str
					Una stringa contenente la risposta del modello all' interazione effettuata

			Raises
			------
				AccessorNotInitedError
					Si verifica se questo ILlmApiAccessor non è stato inizializzato
			
				ChatNeverSelectedError
					Si verifica se non è mai stato impostato un oggetto chat da utilizzare
			
				ModelNotSelectedError
					Si verifica se non è stato selezionato nessun modello per questo ILlmApiAccessor
					
				ValueError
					Si verifica se `user_prompt` ha valore None
	
				InvalidPromptError
					Si verifica se `user_prompt` è invalido per l' API rappresentata
				
				ApiConnectionError
					Si verifica se avviene un errore di connessione con la piattaforma di inferenza
					appartenente al suo dominio.
					Nel caso in cui questo errore riguardi un timeout connessione viene fornito,
					nell' attributo `args[0]`, la stringa "timeout"
				
				ResponseTimedOutError
					Si verifica se scatta il tempo `timeout` indicato e non è stata ricevuta
					alcuna parte della risposta
					
				ApiResponseError
					Si verifica se la richiesta fornita all' API produce un errore di risposta
					appartenente al suo dominio.
					Nel caso di un errore sconosciuto viene fornita, nell' attributo `args`,
					la stringa `"unknown"`
					
				SaturatedContextWindowError
					Si verifica se viene saturata la finestra di contesto durante l' interazione
		"""
		pass