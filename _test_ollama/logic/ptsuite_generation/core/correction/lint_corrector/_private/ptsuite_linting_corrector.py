from typing import Tuple

# ============= RegEx Utilities ============ #
from regex import (
	search as reg_search,
	Match,
	RegexFlag as RegexFlags
)
# ========================================== #
from py_compile import (
	compile as py_compile,
	PycInvalidationMode as Pyc_InvMode,
	PyCompileError
)

from ....checking.lint_checker import LintingChecker

from .....llm_access.llm_apiaccessor import ILlmApiAccessor
from .....llm_access.llm_apiaccessor.exceptions import (
	ApiResponseError,
	SaturatedContextWindowError,
	ResponseTimedOutError
)

from ......utils.logger import ATemporalFormattLogger
from ......utils.logger.exceptions import FormatNotSetError

from ....exceptions import (
	PromptingSessionNeverPerformedError,
	PromptingSessionNotStartedError,
	PromptingSessionInProgressError,
	WrongResponseFormatError
)
from ..exceptions import SyntacticallyIncorrectPtsuiteError



class PtsuiteLintingCorrector:
	"""
		Rappresenta un oggetto in grado di effettuare tentativi di correzione, di test-suites parziali,
		dopo averne verificato la correttezza a livello di linting, del loro codice.
		
		La verifica di correttezza, a livello di linting, viene svolta all' interno di un container docker,
		la cui immagine è pre-configurata per essere l' ambiente adatto al corretto funzionamento del progetto focale
		desiderato.
		
		Attributi di Classe Pubblici:
			- `LINTING_TEMP_DIR` (str) : Rappresenta il nome, di default, della directory temporanea, nel container, in cui verranno memorizzati i files usati temporaneamente durante la verifica del codice
			- `LINTING_TOOLS_DIRNAME` (str) : Rappresenta il nome, di default, della directory in cui sono contenuti i tools necessari per la verifica, a livello di linting, che verrà effettuata all' interno dell' ambiente del progetto focale
			- `LINTING_SCRIPT` (str) : Rappresenta il nome, di default, dello script Python, contenuto della directory dei tools per la verifica a livello di linting, che eseguirà la verifica nell' ambiente del progetto focale tramite gli strumenti scelti
			- `GENCODE_PATT` (str) : Rappresenta il pattern regex, di default, da utilizzare per identificare il codice nella risposta di un tentativo di correzione
	"""
	
	LINTING_TEMP_DIR: str = "gtsai_linting_temp"
	LINTING_TOOLS_DIR: str = "gtsai_linting_tools"
	LINTING_SCRIPT: str = "exec_linting_check.py"
	GENCODE_PATT: str = r"```python\n?(?P<gen_code>[\s\S]+)\n?```"
	
	def __init__(
			self,
			max_tries: int,
			llm_accsor: ILlmApiAccessor,
			lint_checker: LintingChecker,
			resp_format: str = None,
			logger: ATemporalFormattLogger = None,
	):
		"""
			Costruisce un nuovo PtsuiteLintingCorrector associandolo ad un `ILlmApiAccessor`
			con cui effettuerà le richieste di correzione ai LLMs che gli verranno, o sono stati,
			impostati.
			
			Eventualmente viene anche associato al logger utilizzato per registrare le fasi di ogni
			tentativo di generazione, e al formato di risposta differente da quello di default
			(formato di default: `self.GENCODE_PATT`)

			Parameters
			----------
				max_tries: int
					Un intero che indica il numero di tentativi massimi da effettuare
					nelle richieste
			
				llm_accsor: ILlmApiAccessor
					Un oggetto `ILlmApiAccessor` che verrà utilizzato per effettuare le richieste di correzione
					
				lint_checker: str
					Un oggetto `LintingChecker` rappresentante il verificatore di linting da utilizzare
					per testare la correttezza della test-suite parziale dopo ogni tentativo
					
				resp_format: str
					Opzionale. Default = `None`. Una stringa RegEx contenente il formato da utilizzare per identificare
					il codice derivante dai tentativi di correzione effettuati.
					E' necessario che contenga un named group chiamato "gen_code"
					
				logger: ATemporalFormattLogger
					Opzionale. Default = `None`. Un oggetto `ATemporalFormattLogger` rappresentante l' eventuale logger
					da utilizzare per registrare le fasi di ogni tentativo di correzione (non per registrare le fasi
					della richiesta al LLM)
					
			Raises
			------
				ValueError
					Si verfica se:
					
						- Il parametro `max_tries` è minore di 1
						- Il parametro `response_format` viene fornito ma non contiene un named group che si chiama "gen_code"
		"""
		if max_tries < 1:
			raise ValueError()
		
		self._resp_regex: str =	self.GENCODE_PATT
		if resp_format is not None:
			if resp_format.find("(?P<gen_code>") == -1:
				raise ValueError()
			self._resp_regex = resp_format
		
		# Attributi per la gestione della serie di correzioni
		self._corr_everperf: bool = False
		self._corr_inprogr: bool = False
		self._max_tries: int = max_tries
		self._times_tried: int = 0
		self._try_succ: bool = False
		self._resp_tout: int = 0
		
		# Attributi riguardanti ogni tentativo di correzione
		self._last_corrpts: str = ""
		self._max_tries: int = max_tries
		self._llm_platf: ILlmApiAccessor = llm_accsor
		
		# Verificatore di linting delle test-suite parziali
		self._lint_chker: LintingChecker = lint_checker
		
		# Logger da utilizzare per loggare gli steps di ogni tentativo
		self._logger: ATemporalFormattLogger = logger
		
		
	def has_corr_terminated(self) -> bool:
		"""
			Verifica se la serie di tentativi di correzione in corso è terminata
			o per riuscita della correzione, o per raggiungimento dei tentativi massimi
			
			Returns
			-------
				bool
					Un booleano che indica se la serie di tentativi iniziata precedentemente,
					è terminata
					
			Raises
			------
				PromptingSessionNeverPerformedError
					Si verifica se non è mai stata iniziata una serie di tentativi
					di correzione
		"""
		if not self._corr_everperf:
			raise PromptingSessionNeverPerformedError()
		
		return not self._corr_inprogr


	def has_corr_succ(self) -> bool:
		"""
			Verifica se l' ultimo tentativo di generazione effettuato ha avuto successo
			così da riuscire a generare una test-suite parziale

			Returns
			-------
				bool
					Un booleano che indica se l' ultima test-suite parziale di cui
					è stata tentata la generazione è riuscita

			Raises
			------
				PromptingSessionNeverPerformedError
					Si verifica se non è mai stata eseguita nessuna serie di tentativi
			
				PromptingSessionInProgressError
					Si verifica se non è in corso una serie di tentativi di correzione
		"""
		if not self._corr_everperf:
			raise PromptingSessionNeverPerformedError()
		if self._corr_inprogr:
			raise PromptingSessionInProgressError()
		
		return not self._try_succ
	
	
	def get_lastcorr(self) -> Tuple[str, int]:
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
					Si verifica se non è mai stata eseguita nessuna serie di tentativi
			
				PromptingSessionInProgressError
					Si verifica se è in corso una serie di tentativi di correzione
		"""
		if not self._corr_everperf:
			raise PromptingSessionNeverPerformedError()
		if self._corr_inprogr:
			raise PromptingSessionInProgressError()
		
		result: Tuple[str, int] = tuple()
		if self._last_corrpts is not None:
			result = (self._last_corrpts, self._times_tried)
		
		return result


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
				
				SyntacticallyIncorrectPtsuiteError
					Si verifica se il codice della test-suite parziale data è incorretto
					sintatticamente
		"""
		if self._corr_inprogr:
			raise PromptingSessionInProgressError()
		
		# Check sintattico della test-suite parziale
		try:
			py_compile(
				ptsuite_code,
				doraise=True,
				invalidation_mode=Pyc_InvMode.TIMESTAMP
			)
		except PyCompileError as err:
			raise SyntacticallyIncorrectPtsuiteError()
		
		if not self._corr_everperf:
			self._corr_everperf = True
		self._corr_inprogr = True
		
		# Impostazione delle variabili condivise relative al singolo tentativo
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
			logger_frmt = "[PtsuiteLintingCorrector] {message} " + def_time_format
		self._logger.set_format(logger_frmt)
	
	
	def perform_corr_try(self) -> str:
		"""
			Effettua un singolo tentativo di correzione di una test-suite parziale di una specifica entità
			(funzione o metodo) richiedendola ad uno specifico Large Language Model.
			
			ASSUNZIONE: Si assume che il prompt di richiesta, per la correzione, sia stato impostato nell' oggetto
			chat associato all' `ILlmApiAccessor` fornito a questo correttore
			
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
					
				LintingCheckNotPerformedError
					Si verifica se non è stata eseguita la verifica di linting dell' ultima versione della
					test-suite parziale prima di chiamare quest' operazione
				
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
				
				OSError
					Se si verificano problemi con l' apertura, o scrittura, nel file temporaneo utilizzato
					per la verifica
		"""
		if not self._corr_inprogr:
			raise PromptingSessionNotStartedError()
		
		corrtry_ptsuite: str = None
		if self._is_linting_correct():
			self._try_succ = True
		if (not self._try_succ) and (self._times_tried <= self._max_tries):
			try:
				self._logger.log(
					f"Inizio della richiesta di correzione di linting (Tentativo {self._times_tried}/{self._max_tries}) ..."
				) if self._logger is not None else None
				response: str = self._llm_platf.prompt(self._resp_tout)
				
				resp_match: Match[str] = reg_search(self._resp_regex, response, RegexFlags.MULTILINE)
				if resp_match is None:
					raise WrongResponseFormatError()
				self._last_corrpts = resp_match.group("gen_code")
				
				self._logger.log("Fine della richiesta di correzione") if self._logger is not None else None
				
				self._logger.log("Verifica di linting post-tentativo di correzione ...") if self._logger is not None else None
				is_lint_correct = self._is_linting_correct()
				if is_lint_correct:
					# Tentativo di correzione riuscito
					self._logger.log(
						f"Test-suite parziale corretta con successo al tentativo {self._times_tried}/{self._max_tries}"
					) if self._logger is not None else None
					self._try_succ = True
					self._corr_inprogr = False
					self._lint_chker.clear_resources()
					self._logger.log("La serie di tentativi di correzione è terminata con successo") if self._logger is not None else None
				else:
					# Tentativo di correzione fallito
					self._logger.log("La test-suite parziale non è stata corretta") if self._logger is not None else None
			except (ApiResponseError,
			        SaturatedContextWindowError,
			        ResponseTimedOutError):
				# Richiesta al LLM di correzione fallita
				self._times_tried += 1
		else:
			if (self._times_tried <= self._max_tries):
				# Tutti i tentativi sono stati esauriti
				self._logger.log("La serie di tentativi di correzione è terminata fallendo") if self._logger is not None else None
				self._last_corrpts = None
			self._corr_inprogr = False
			self._lint_chker.clear_resources()
	
		return corrtry_ptsuite
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================
	
	
	def _is_linting_correct(self) -> bool:
		"""
			Effettua la verifica di correttezza a livello di linting sull' ultima
			test-suite parziale prodotta
		"""
		if len(self._lint_chker.check_lintically(self._last_corrpts).keys()) == 0:
			return True
		else:
			return False