from typing import Tuple

# ============= RegEx Utilities ============ #
from regex import (
	search as reg_search,
	Match,
	RegexFlag as RegexFlags,
)
# ========================================== #

from .....llm_access.llm_apiaccessor import ILlmApiAccessor
from .....llm_access.llm_apiaccessor.exceptions import (
	ApiResponseError,
	ResponseTimedOutError,
	SaturatedContextWindowError
)

from ....checking.synt_checker import ISyntacticChecker

from ......utils.logger import ATemporalFormattLogger
from ......utils.logger.exceptions import FormatNotSetError

from ....exceptions import (
	WrongResponseFormatError,
	PromptingSessionNeverPerformedError,
	PromptingSessionInProgressError,
	PromptingSessionNotStartedError
)



class PtsuiteSyntacticCorrector:
	"""
		Rappresenta un oggetto in grado di effettuare la correzione sintattica di test-suites parziali
		richiedendola a un LLM.
		Succesivamente alla richiesta di correzione, viene verificata la correttezza sintattica della
		test-suite parziale tramite un tool di verifica.
		
		Attributi di Classe Pubblici:
			- `GENCODE_PATT` (str) : Rappresenta il pattern regex, di default, da utilizzare per identificare il codice nella risposta di un tentativo di correzione
	"""
	
	GENCODE_PATT: str = r"```python\n?(?P<gen_code>[\s\S]+)\n?```"
	
	def __init__(
			self,
			max_tries: int,
			llm_accsor: ILlmApiAccessor,
			synt_checker: ISyntacticChecker,
			resp_format: str = None,
			logger: ATemporalFormattLogger = None
	):
		"""
			Costruisce un nuovo PtsuiteSyntacticCorrector associandolo al numero massimo di
			tentativi da effettuare per ogni serie di correzioni
			
			Parameters
			----------
				max_tries: int
					Un intero che indica il numero di tentativi massimi da
					effettuare nelle richieste
					
				llm_accsor: ILlmApiAccessor
					Un oggetto `ILlmApiAccessor` che verrà utilizzato per effettuare le richieste di correzione
					
				synt_checker: str
					Un oggetto `ISyntacticChecker` rappresentante il verificatore sintattico da utilizzare
					per testare la correttezza della test-suite parziale dopo ogni tentativo
					
				resp_format: str
					Opzionale. Default = `None`. Una stringa RegEx contenente il formato da utilizzare
					per identificare il codice derivante dai tentativi di correzione effettuati.
					E' necessario che contenga un named group chiamato "gen_code"
					
				logger: ATemporalFormattLogger
					Opzionale. Default = `None`. Un oggetto `ATemporalFormattLogger` rappresentante l' eventuale logger
					da utilizzare per registrare le fasi di ogni tentativo di correzione (non per registrare le fasi
					della richiesta al LLM)
					
			Raises
			------
				ValueError
					Si verifica se il parametro `llm_accsor` ha valore `None`
		"""
		if max_tries < 1:
			raise ValueError()
		
		self._resp_regex: str =	self.GENCODE_PATT
		if resp_format is not None:
			if resp_format.find("(?P<gen_code>") == -1:
				raise ValueError()
			self._resp_regex = resp_format

		self._corr_everperf: bool = False
		self._corr_inprogr: bool = False
		
		self._max_tries: int = max_tries
		self._times_tried: int = 0
		
		self._last_syntcheck: Tuple[str, str] = None
		self._last_corrpts: str = None
		self._try_succ: bool = False
		self._resp_tout: int = 0
		
		self._proj_name: str = None
		self._module_name: str = None
		
		self._llm_platf: ILlmApiAccessor = llm_accsor
		self._synt_chker: ISyntacticChecker = synt_checker
		
		self._logger: ATemporalFormattLogger = logger
	
	
	def has_corr_terminated(self) -> bool:
		"""
			Verifica se l' ultima serie di tentativi di correzione avviata è terminata
			o per riuscita della correzione, o per raggiungimento dei tentativi massimi
			
			Returns
			-------
				bool
					Un booleano che indica se la serie di tentativi iniziata precedentemente,
					è terminata
					
			Raises
			------
				PromptingSessionNeverPerformedError
					Si verifica se non è mai stata iniziata una serie di tentativi di correzione
		"""
		if not self._corr_everperf:
			raise PromptingSessionNeverPerformedError()
		
		return not self._corr_inprogr
	
	
	def has_corr_succ(self) -> bool:
		"""
			Verifica se l' ultimo tentativo di generazione effettuato, della serie di tentativi
			terminata, ha avuto successo così da riuscire a generare una test-suite parziale

			Returns
			-------
				bool
					Un booleano che indica se l' ultima test-suite parziale di cui
					è stata tentata la generazione è riuscita

			Raises
			------
				PromptingSessionNeverPerformedError
					Si verifica se non è mai stata iniziata una serie di tentativi di correzione
			
				PromptingSessionInProgressError
					Si verifica se non è in corso una serie di tentativi di correzione
		"""
		if not self._corr_everperf:
			raise PromptingSessionNeverPerformedError()
		if self._corr_inprogr:
			raise PromptingSessionInProgressError()
		
		return not self._try_succ
	
	
	def get_lastcorr(self) -> str:
		"""
			Restituisce una tupla contenente:
				
				- Il codice risultante dall' ultimo tentativo di correzione di una test-suite parziale
				- Il numero di tentativo in cui ha avuto successo la correzione

			Per verificare la buona riuscita dell' ultima serie di tentativi è necessario utilizzare
			l'operazione `.has_corr_succ(...)`
			
			Returns
			-------
				Tuple[str, int]
					Una tupla variegata contenente:
						- Il codice dell' ultimo tentativo di correzione dell' ultima test-suite parziale
						  di cui è stata tentata la correzione
						- Il numero di tentativo in cui ha avuto successo la correzione
					
					Viene restituita una tupla vuota se l' ultima serie di tentativi non è andata a
					buon fine
		
			Raises
			------
				PromptingSessionNeverPerformedError
					Si verifica se non è mai stata iniziata una serie di tentativi di correzione
			
				PromptingSessionInProgressError
					Si verifica se è in corso una serie di tentativi di correzione
		"""
		if not self._corr_everperf:
			raise PromptingSessionNeverPerformedError()
		if self._corr_inprogr:
			raise PromptingSessionInProgressError()
		
		return self._last_corrpts
	
	
	def start_new_correction(
			self,
			ptsuite_code: str,
			resp_timeout: int
	):
		"""
			Inizia una nuova serie di tentativi di correzione di una test-suite parziale
			azzerando i risultati della serie di correzione precedente.
			La riuscita finale della correzione NON è garantita.
			
			Parameters
			----------
				ptsuite_code: str
					Una stringa contenente il codice della test-suite parziale di cui
					effettuare i tentativi di correzione
				
				resp_timeout: int
					Un intero rappresentante il timeout in millisecondi dopo il quale
					dichiarare la risposta fallita
					
			Raises
			------
				PromptingSessionInProgressError
					Si verifica se è stata già iniziata una serie di tentativi di correzione
					senza essere terminata
					
				ValueError
					Si verifica se:
					
						- Il parametro `ptsuite_code` ha valore `None` o è una stringa vuota
						- Il parametro `resp_timeout` ha valore minore di 1
		"""
		if (ptsuite_code is None) or (ptsuite_code == ""):
			raise ValueError()
		if resp_timeout < 1:
			raise ValueError()
		if self._corr_inprogr:
			raise PromptingSessionInProgressError()
		
		if not self._corr_everperf:
			self._corr_everperf = True
		self._corr_inprogr = True
		
		self._times_tried = 1
		self._try_succ = False
		self._last_corrpts = ptsuite_code
		self._resp_tout = resp_timeout
		
		# Setup del formato del logger
		def_time_format: str = "( {day}-{month}-{year} | {hour}:{min}:{second} )"
		logger_frmt: str
		try:
			logger_frmt = self._logger.unset_format()
		except FormatNotSetError:
			logger_frmt = "[LoggableSyntCorrector] {message} " + def_time_format
		self._logger.set_format(logger_frmt)
	
	
	def perform_corr_try(self) -> str:
		"""
			Effettua un singolo tentativo di correzione di una test-suite parziale di una specifica entità
			(funzione o metodo) richiedendola ad uno specifico Large Language Model.
			
			ASSUNZIONE: Si assume che il prompt di richiesta sia stato impostato nell' oggetto chat
			associato all' `ILlmApiAccessor` fornito a questo ISyntCorrector
			
			Returns
			-------
				str
					Una stringa contenente l' ultima test-suite parziale prodotta dalla richiesta
					di correzione effettuata in questo tentativo.
					Se la richiesta è stata interrotta per un errore viene restituito il valore `None`
			
			Raises
			------
				PromptingSessionNotStartedError
					Si verifica se non è stata iniziata una serie di tentativi di correzione
				
				ChatNeverSelectedError
					Si verifica se non è stato mai associato una chat all' `ILlmApiAccessor` fornito
			
				ModelNotSelectedError
					Si verifica se non è stato selezionato nessun modello per l' `ILlmApiAccessor` fornito
					
				ApiConnectionError
					Si verifica se avviene un errore di connessione con la piattaforma di inferenza.
					L' errore è appartenente al suo dominio.
					Si utilizza l' attributo `args[0]`, di tipo stringa, per distinguere la natura dell' errore:
					
						- "timeout": La natura dell' errore riguarda il timeout di connesione
						- "other": La natura dell' errore è di altro tipo (comprensibile dalle altre componenti di `args`)
					
				InvalidPromptError
					Si verifica se il prompt di richiesta è invalido per l' API rappresentata dall'
					`ILlmApiAccessor` fornito
					
				WrongResponseFormatError
					Si verifica se il formato di risposta non è conforme al formato associato
					a questo ISyntCorrector
		"""
		if not self._corr_inprogr:
			raise PromptingSessionNotStartedError()
		
		corrtry_ptsuite: str = None
		if self._is_syntact_correct():
			self._try_succ = True
		if (not self._try_succ) and (self._times_tried <= self._max_tries):
			try:
				self._logger.log(
					f"Inizio della richiesta di correzione sintattica (Tentativo {self._times_tried}/{self._max_tries}) ..."
				) if self._logger is not None else None
				
				response: str = self._llm_platf.prompt(self._resp_tout)
				
				resp_match: Match[str] = reg_search(self._resp_regex, response, RegexFlags.MULTILINE)
				if resp_match is None:
					raise WrongResponseFormatError()
				self._last_corrpts = resp_match.group("gen_code")
				corrtry_ptsuite = self._last_corrpts
				
				self._logger.log("Fine della richiesta di correzione") if self._logger is not None else None
				
				is_synt_corr = self._is_syntact_correct()
				if is_synt_corr:
					# Tentativo di correzione riuscito
					self._logger.log(
						f"Test-suite parziale corretta con successo al tentativo {self._times_tried}/{self._max_tries}"
					) if self._logger is not None else None
					self._logger.log("La serie di tentativi di correzione è terminata con successo") if self._logger is not None else None
					self._try_succ = True
					self._corr_inprogr = False
				else:
					# Tentativo di correzione fallito
					self._logger.log("La test-suite parziale non è stata corretta") if self._logger is not None else None
			except (ApiResponseError,
			        SaturatedContextWindowError,
			        ResponseTimedOutError) as error:
				# Richiesta al LLM di correzione fallita
				self._logger.log(f"La test-suite parziale non è stata corretta (Errore: {str(type(error))})") if self._logger is not None else None
				self._times_tried += 1
		else:
			if (self._times_tried > self._max_tries):
				# Tutti i tentativi sono stati esauriti
				self._last_corrpts = None
				self._logger.log("La serie di tentativi di correzione è terminata fallendo") if self._logger is not None else None
			self._corr_inprogr = False
		
		return corrtry_ptsuite
			
			
	def _pf__get_curr_ptsuite(self) -> str:
		"""
			Restituisce la test-suite parziale che deriva dall' ultima richiesta
			effettuata con successo
			
			Returns
			-------
				str
					Una stringa contenente la test-suite parziale derivante dall' ultima
					richiesta, alla piattaforma di inferenza, effettuata con successo
		"""
		return self._last_corrpts
	
	
	def _pf__get_max_tries(self) -> int:
		"""
			Restituisce il numero di tentativi massimi da effettuare
			
			Returns
			-------
				int
					Un intero che indica il numero di tentativi massimi di correzione sintattica
		"""
		return self._max_tries
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	def _p__try_start(self, try_num: int):
		"""
			Esegue le eventuali operazioni necessarie all' inizio di un tentativo
			di correzione.
			
			L' implementazione di default è vuota
			
			Parameters
			----------
				try_num: int
					Un intero che indica il tentativo di correzione attuale
					che ha avuto successo
		"""
		pass
	
	
	def _p__post_response(self):
		"""
			Esegue le eventuali operazioni necessarie alla fine della richiesta di correzione
			da parte del Large Language model.
			
			E' garantito all' interno di questo metodo:
				
				- Che la test-suite parziale è stata prodotta dal LLM
				- Che la test-suite parziale prodotta dal LLM è stata impostata come tentativo
				  più recente di correzione
			
			L' implementazione di default è vuota
		"""
		pass
	
	
	def _p__try_endsucc(self, try_num: int):
		"""
			Esegue le eventuali operazioni necessarie se il tentativo di correzione,
			in cui è chiamato, termina correggendo con successo la test-suite parziale.
			
			L' implementazione di default è vuota
			
			Parameters
			----------
				try_num: int
					Un intero che indica il tentativo di correzione attuale
					che ha avuto successo
		"""
		pass
	
	
	def _p__try_endfail(self, try_num: int):
		"""
			Esegue le eventuali operazioni necessarie se il tentativo di correzione,
			in cui è chiamato, termina fallendo la correzione della test-suite parziale.
			
			L' implementazione di default è vuota
			
			Parameters
			----------
				try_num: int
					Un intero che indica il tentativo di correzione attuale che
					non ha avuto successo
		"""
		pass
	
	
	def _p__req_endfail(
			self,
	        try_num: int,
			error_name: str
	):
		"""
			Esegue le eventuali operazioni necessarie se la richiesta del tentativo
			di correzione, in cui è chiamato, termina fallendo.
			
			L' implementazione di default è vuota
			
			Parameters
			----------
				try_num: int
					Un intero che indica il tentativo di correzione attuale che
					non ha avuto successo
					
				error_name: str
					Una stringa contenente il nome dell' errore verificatosi durante la
					richiesta di correzione
		"""
		pass
	
	
	def _p__corr_failed(self):
		"""
			Esegue le eventuali operazioni necessarie se l' intera serie di tentativi
			di correzione da cui è chiamato fallisce.
			
			L' implementazione di default è vuota
		"""
		pass
	
	
	def _is_syntact_correct(self) -> bool:
		"""
			Effettua la verifica di correttezza sintattica sull' ultima test-suite parziale
			prodotta
		"""
		if len(self._synt_chker.check_synt(self._last_corrpts)) == 0:
			return True
		else:
			return False