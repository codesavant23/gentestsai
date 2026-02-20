from .. import ILlmApiAccessor

from .....utils.logger import ATemporalFormattLogger

from .._private.ollama_llmapiacc import OllamaLlmApiAccessor



class LlmApiAccessorFactory:
	"""
		Rappresenta una factory per ogni `ILlmApiAccessor`
	"""


	@classmethod
	def for_ollama(
			cls,
			address: str,
	        auth: str,
	        conn_timeout: int,
	        logger: ATemporalFormattLogger | None = None,
	        log_resp: bool = False,
	        logger_sep: str = "\n"
	) -> ILlmApiAccessor:
		"""
			Istanzia un nuovo accessor per la piattaforma di inferenza "Ollama"
			
			Parameters
			----------
				address: str
					Una stringa contenente l' indirizzo (URL assoluto, IPv4 o IPv6) che identifica
					il server su cui è ospitata la piattaforma di inferenza
					
				auth: str
					Una stringa contenente le credenziali di accesso, come coppia `user:token`,
					da utilizzare per le interazioni
					
				conn_timeout: int
					Un intero rappresentante il timeout in millisecondi dopo il quale
					dichiarare un tentativo di connessione fallito
					
				logger: ATemporalFormattLogger
					Opzionale. Default = `None`. Un oggetto `ATemporalFormattableLogger` rappresentante
					il logger da utilizzare per registrare i passaggi effettuati da questo OllamaLlmApiAccessor
					durante ogni richiesta effettuata
					
				logger_sep: str
					Opzionale. Default = `\\n`. Una stringa contenente il separatore da utilizzare per i
					messaggi di logging che verranno registrati.
					
				log_resp: bool
					Opzionale. Default = `False`. Un booleano che indica se è necessario loggare anche
					i "chunks" della risposta che vengono ricevuti
					
			Returns
			-------
				ILlmApiAccessor
					Un oggetto `ILlmApiAccessor` che permette l' accesso alla piattaforma
					di inferenza "Ollama
					
			Raises
			------
				ValueError
					Si verifica se:
						
						- Almeno uno tra `address` e `auth` hanno valore `None`
						- Il parametro `log_resp` ha valore `True` ma non è stato fornito un logger
		"""
		return OllamaLlmApiAccessor(
			address, auth,
			conn_timeout,
			logger, log_resp, logger_sep
		)
		
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================