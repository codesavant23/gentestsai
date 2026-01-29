# ============= RegEx Utilities ============ #
from regex import (
	search as reg_search,
	Match,
	RegexFlag as RegexFlags,
)
# ========================================== #

from .....utils.logger import ATemporalFormattLogger

from ....llm_access.llm_apiaccessor import ALoggableLlmApiAccessor
from ....llm_access.llm_apiaccessor.exceptions import (
	ResponseTimedOutError,
	ApiResponseError,
	SaturatedContextWindowError,
)

from ...exceptions import WrongResponseFormatError
from ..exceptions import (
	GenerationInProgressError,
	GenerationNotStartedError,
	GenerationNeverPerformedError
)



class EntityPTsuiteGenerator:
	"""
		Rappresenta un oggetto in grado di richiedere ad un LLM di generare una test-suite parziale,
		relativa ad una singola entità di codice.

		Con “entità” si intende la più piccola unità di codice la cui semantica può essere formalizzata
		in un contratto (una funzione o un metodo di classe).
		Queste unità elementari rappresentano la granularità minima significativa per verifiche
		automatiche e permettono di isolare test specifici senza coinvolgere (direttamente)
		l’intera classe o modulo.
			
		Attributi di Classe Pubblici:
			- `GENCODE_PATT` (str) : Rappresenta il pattern regex, di default, da utilizzare per identificare il codice nella risposta di un tentativo di generazione
	"""
	GENCODE_PATT: str = r"```python\n?(?P<gen_code>[\s\S]+)\n?```"

	def __init__(
			self,
			max_tries: int,
			llm_accsor: ALoggableLlmApiAccessor,
			logger: ATemporalFormattLogger = None,
			response_format: str = None
	):
		"""
			Costruisce un nuovo EntityPTsuiteGenerator associandolo ad un `ALoggableLlmApiAccessor`
			con cui effettuerà le richieste di generazione ai LLMs che gli sono/verranno impostati

			Parameters
			----------
				max_tries: int
					Un intero che indica il nuovo numero di tentativi massimi da
					effettuare nelle richieste
			
				llm_accsor: ALoggableLlmApiAccessor
					Un oggetto `ALoggableLlmApiAccessor` che verrà utilizzato per effettuare le richieste di generazione
					
				logger: ATemporalFormattLogger
					Opzionale. Default = `None`. Un oggetto `ATemporalFormattLogger` rappresentante l' eventuale logger
					da utilizzare per registrare le fasi di ogni tentativo di generazione (non per registrare le fasi
					della richiesta al LLM di ogni tentativo)
					
				response_format: str
					Opzionale. Default = `None`. Una stringa RegEx contenente il formato da utilizzare per identificare
					il codice derivante dai tentativi di generazione effettuati.
					E' necessario che contenga un named group chiamato "gen_code"
					
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
		if response_format is not None:
			if response_format.find("(?P<gen_code>") == -1:
				raise ValueError()
			self._resp_regex = response_format
		
		self._gen_everperf: bool = False
		self._gen_inprogr: bool = False
		self._times_tried: int = 0
		self._try_succ: bool = False
		self._resp_tout: int = 0
		
		self._last_genresp: str = ""
		self._max_tries: int = max_tries
		
		self._llm_platf: ALoggableLlmApiAccessor = llm_accsor
		self._logger: ATemporalFormattLogger = logger
		
		
	def has_gen_terminated(self) -> bool:
		"""
			Verifica se la serie di tentativi di generazione in corso è terminata
			o per riuscita della generazione, o per raggiungimento dei tentativi massimi
			
			Returns
			-------
				bool
					Un booleano che indica se la serie di tentativi iniziata precedentemente,
					è terminata
		"""
		if not self._gen_everperf:
			raise GenerationNeverPerformedError()
		
		return not self._gen_inprogr
	
	
	def has_gen_succ(self) -> bool:
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
				GenerationInProgressError
					Si verifica se
		"""
		if self._gen_inprogr:
			raise GenerationInProgressError()
		if not self._gen_everperf:
			raise GenerationNeverPerformedError()
		
		return not self._try_succ


	def get_lastgen(self) -> str:
		"""
			Restituisce il codice risultante dall' ultimo tentativo di generazione di una test-suite parziale.

			Per verificare la correttezza del codice restituito è necessario utilizzare l'operazione
			`.has_corr_succeeded(...)`

			Returns
			-------
				str
					Una stringa contenente il codice dell' ultimo tentativo di correzione dell' ultima test-suite parziale
					di cui è stata tentata la correzione

			Raises
			------
				InvalidPreviousGenerationError
					Si verifica se:

						- Si tenta di eseguire quest' operazione quando non è mai stato effettuata nessuna richiesta di correzione in precedenza
						- Si tenta di eseguire quest' operazione quando l' ultima richiesta di correzione è terminata con un' eccezione
		"""
		if self._gen_inprogr:
			raise GenerationInProgressError()
		if not self._gen_everperf:
			raise GenerationNeverPerformedError()
		
		gen_code: str = ""
		if self._last_genresp is not None:
			gen_code = reg_search(
				self._resp_regex,
				self._last_genresp,
				RegexFlags.MULTILINE
			).group("gen_code")
		
		return gen_code
		
		
	def start_new_generation(
			self,
			resp_timeout: int
	):
		"""
			Inizia una nuova serie di tentativi di generazione di una test-suite parziale
			azzerando i risultati della serie di generazione precedente.
			La riuscita finale della generazione NON è garantita.
			
			Parameters
			----------
				resp_timeout: int
					Un intero rappresentante il timeout in millisecondi dopo il quale
					dichiarare la risposta fallita
					
			Raises
			------
				GenerationInProgressError
					Si verifica se è stata già iniziata una serie di tentativi di generazione
					senza essere terminata
		"""
		if self._gen_inprogr:
			raise GenerationInProgressError()
		
		if not self._gen_everperf:
			self._gen_everperf = True
		self._gen_inprogr = True
		
		self._times_tried = 1
		self._try_succ = False
		self._last_genresp = None
		self._resp_tout = resp_timeout
		if self._logger is not None:
			self._logger.log(
				f"Inzio di una nuova serie di tentativi di generazione"
			)
		
		
	def perform_gen_try(self):
		"""
			Effettua un singolo tentativo di generazione di una test-suite parziale di una specifica entità
			(funzione o metodo) richiedendola ad uno specifico Large Language Model.
			
			ASSUNZIONE: Si assume che il prompt di richiesta sia stato impostato nell' oggetto chat
			associato all' `ALoggableLlmApiAccessor` fornito a questo EntityPTsuiteGenerator
			
			Raises
			------
				GenerationNotStartedError
					Si verifica se non è stata iniziata una serie di tentativi di generazione
				
				ChatNeverSelectedError
					Si verifica se non è stato mai associato una chat all' `ALoggableLlmApiAccessor` fornito
			
				ModelNotSelectedError
					Si verifica se non è stato selezionato nessun modello per l' `ALoggableLlmApiAccessor` fornito
					
				ApiConnectionError
					Si verifica se avviene un errore di connessione con la piattaforma di inferenza.
					L' errore è appartenente al suo dominio.
					Si utilizza l' attributo `args[0]`, di tipo stringa, per distinguere la natura dell' errore:
					
						- "timeout": La natura dell' errore riguarda il timeout di connesione
						- "other": La natura dell' errore è di altro tipo (comprensibile dalle altre componenti di `args`)
					
				InvalidPromptError
					Si verifica se il prompt di richiesta è invalido per l' API rappresentata dall'
					`ALoggableLlmApiAccessor` fornito
					
				WrongResponseFormatError
					Si verifica se il formato di risposta di almeno uno dei tentativi di generazione
					non è conforme al formato associato a questo EntityPTsuiteGenerator (o di default)
		
		"""
		if not self._gen_inprogr:
			raise GenerationNotStartedError()
		
		if (not self._try_succ) and (self._times_tried <= self._max_tries):
			try:
				if self._logger is not None:
					self._logger.log(
						f"Inzio del tentativo di generazione no. {self._times_tried}/{self._max_tries}"
					)
					
				response = self._llm_platf.prompt(self._resp_tout)
				
				resp_match: Match[str] = reg_search(self._resp_regex, response)
				if resp_match is None:
					raise WrongResponseFormatError()
				
				self._last_genresp = resp_match.group("gen_code")
				self._try_succ = True
				
				if self._logger is not None:
					self._logger.log(
						f"Tentativo di generazione no. {self._times_tried}/{self._max_tries} riuscito con successo"
					)
			except (ApiResponseError, SaturatedContextWindowError,
			        ResponseTimedOutError):
				self._times_tried += 1
		else:
			self._gen_inprogr = False
			if self._logger is not None:
				self._logger.log(
					f"Fine della serie di tentativi di generazione"
				)