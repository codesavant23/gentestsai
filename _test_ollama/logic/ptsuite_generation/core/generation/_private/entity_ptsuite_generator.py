# ============== OS Utilities ============== #
from os import remove as os_remove
# ========================================== #
# ============= RegEx Utilities ============ #
from regex import (
	search as reg_search,
	Match,
	RegexFlag as RegexFlags,
)
# ========================================== #

from ....llm_access.llm_apiaccessor import ALoggableLlmApiAccessor
from ....llm_access.llm_apiaccessor.exceptions import (
	ResponseTimedOutError,
	ApiResponseError,
	SaturatedContextWindowError,
)

from ...exceptions import WrongResponseFormatError
from ..exceptions import InvalidPreviousGenerationError



class EntityPartialTsuiteGenerator:
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
			response_format: str = None
	):
		"""
			Costruisce un nuovo EntityPartialTsuiteGenerator associandolo ad un `ALoggableLlmApiAccessor`
			con cui effettuerà le richieste di generazione ai LLMs che gli sono/verranno impostati

			Parameters
			----------
				max_tries: int
					Un intero che indica il nuovo numero di tentativi massimi da
					effettuare nelle richieste
			
				llm_accsor: ALoggableLlmApiAccessor
					Un oggetto `ALoggableLlmApiAccessor` che verrà utilizzato per effettuare le richieste di generazione
					
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
		
		self._tried_generation: bool = False
		self._skipped: bool = False
		
		self._last_genresp: str = ""
		self._tempfile_path: str = None
		self._max_tries: int = max_tries
		self._llm_platf: ALoggableLlmApiAccessor = llm_accsor
		

	def has_gen_succeeded(self) -> bool:
		"""
			Verifica se l' ultima generazione effettuata ha avuto successo così da riuscire
			a generare una test-suite parziale funzionante

			Returns
			-------
				bool
					Un booleano che indica se l' ultima test-suite parziale di cui è stata tentata la
					generazione è riuscita fornendo una test-suite parziale funzionante

			Raises
			------
				InvalidPreviousGenerationError
					Si verifica se:
						
						- Si tenta di eseguire quest' operazione quando non è mai stato effettuata nessuna richiesta di generazione in precedenza
						- Si tenta di eseguire quest' operazione quando l' ultima richiesta di generazione è terminata con un' eccezione
		"""
		if not self._tried_generation:
			raise InvalidPreviousGenerationError()
		return not self._skipped


	def get_last_generation(self) -> str:
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
		if not self._tried_generation:
			raise InvalidPreviousGenerationError()
		
		gen_code: str = reg_search(
			self._resp_regex,
			self._last_genresp,
			RegexFlags.MULTILINE
		).group("gen_code")
		return gen_code


	def generate_partial_tsuite(
			self,
			resp_timeout: int
	):
		"""
			Genera una test-suite parziale di una specifica entità (funzione o metodo) richiedendola
			ad uno specifico Large Language Model.
			Viene loggato ogni tentativo del processo di generazione
			
			ASSUNZIONE: Si assume che il prompt di richiesta sia stato impostato nell' oggetto chat
			associato all' `ALoggableLlmApiAccessor` fornito a questo EntityPartialTsuiteGenerator

			Parameters
			----------
				resp_timeout: int
					Un intero rappresentante il timeout in millisecondi dopo il quale dichiarare la risposta fallita

			Returns
			-------
				str
					Una stringa contenente il codice della test-suite parziale generata dal LLM

			Raises
			------
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
					non è conforme al formato associato a questo EntityPartialTsuiteGenerator (o di default)
		"""
		self._skipped = False
		self._tried_generation = False
		
		resp_match: Match[str]
		gen_success: bool = False
		times_tried: int = 1	
		while ((not gen_success) and (times_tried <= self._max_tries)):
			try:
				response = self._llm_platf.prompt(resp_timeout)
				
				resp_match = reg_search(self._resp_regex, response)
				if resp_match is None:
					raise WrongResponseFormatError()
				
				self._last_genresp = resp_match.group("gen_code")
				gen_success = True
			except (ApiResponseError, SaturatedContextWindowError,
			        ResponseTimedOutError):
				os_remove(self._tempfile_path)
				times_tried += 1

		self._tried_generation = True
		self._skipped = not gen_success