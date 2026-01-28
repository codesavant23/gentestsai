from abc import ABC, abstractmethod

from ...llm_chat import ILlmChat
from ...llm_specimpl import ILlmSpecImpl
from ...llm_hyperparam import ILlmHyperParam



class ILlmApiAccessor(ABC):
	"""
		Rappresenta un oggetto che permette, tramite l' utilizzo di una qualsiasi API che fornisce LLMs,
		l' interazione con un LLM.

		E' necessario, dopo la creazione di un ILlmApiAccessor, eseguire:
		
			- L' operazione `.set_chat(...)` per l' associazione con la chat da utilizzare per le richieste (inzialmente la prima)
			- L' operazione `.select_model(...)` per la selezione del primo modello con cui avverranno le interazioni

		La specifica API a cui è legato ogni oggetto ILlmApiAccessor è descritta dai discendenti di questa interfaccia.
	"""
		

	@abstractmethod
	def set_chat(
			self,
			chat: ILlmChat,
			erase_now: bool=True,
			erase_model: bool=True
	):
		"""
			Cambia la chat utilizzata per le prossime interazioni tramite questo
			ILlmApiAccessor. Opzionalmente si può scegliere di non cancellare
			i messaggi della chat associata
			
			Parameters
			----------
				chat: ILlmChat
					Un oggetto `ILlmChat` rappresentante la nuova chat da associare per le
					prossime interazioni
					
				erase_now: bool
					Opzionale. Default = `True`. Un booleano che indica se cancellare tutti i messaggi
					dalla nuova chat associata
					
				erase_model: bool
					Opzionale. Default = `True`. Un booleano che indica se cancellare tutti i messaggi
					della nuova chat associata ad ogni cambio di modello
					
			Raises
			------
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
				ChatNeverSelectedError
					Si verifica se non è mai stato impostato un oggetto chat da utilizzare
			
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
				ChatNeverSelectedError
					Si verifica se non è mai stato impostato un oggetto chat da utilizzare
			
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
				ChatNeverSelectedError
					Si verifica se non è mai stato impostato un oggetto chat da utilizzare
			
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
	def prompt(self, timeout: int) -> str:
		"""
			Effettua una singola interazione con il modello selezionato fornendogli il
			prompt dato come argomento

			Parameters
			----------
				timeout: int
					Un intero rappresentante il timeout di risposta (in millisecondi) dopo il quale
					dichiarare la risposta fallita

			Returns
			-------
				str
					Una stringa contenente la risposta del modello all' interazione effettuata

			Raises
			------
				ChatNeverSelectedError
					Si verifica se non è mai stato impostato un oggetto chat da utilizzare
			
				ModelNotSelectedError
					Si verifica se non è stato selezionato nessun modello per questo ILlmApiAccessor
					
				InvalidPromptError
					Si verifica se il prompt di richiesta è invalido per l' API rappresentata
				
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
		pass