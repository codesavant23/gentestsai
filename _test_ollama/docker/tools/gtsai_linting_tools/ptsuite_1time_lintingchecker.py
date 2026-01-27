from typing import List, Dict, Tuple

from pylint.lint import Run as PylRunner
from json import JSONEncoder

from .linterrors_collection import (
	ErrorCollectorPylReporter,
	LintingRelatedProblem
)

from .linterrors_collection.execeptions import LintingNotExecutedError
from exceptions import LintingCheckerAlreadyUsedError



class PartialTsuite1TimeLintingChecker:
	"""
		Rappresenta un verificatore di codice a livello di linting, da utilizzarsi una sola volta, per una
		test-suite parziale appartenente ad uno specifico progetto focale.
		Ogni istanza è pensata per essere utilizzata SOLO all' interno di un container docker pre-configurato come
		ambiente adatto (in dipendenze e configurazione) per ospitare il progetto focale
	"""

	def __init__(
			self,
			full_root: str,
			ptsuite_path: str,
			result_path: str
	):
		"""
			Costruisce un nuovo PartialTsuite1TimeLintingChecker associandolo alla test-suite parziale di cui effettuare
			la verifica a livello di linting.
			
			Parameters
			----------
				full_root: str
					Una stringa contenente la Full Project Root Path (nel container) del progetto
					focale di cui si verificherà la test-suite parziale
			
				ptsuite_path: str
					Una stringa contenente la path, relativa alla Full Project Root Path nel container, del file
					in cui è scritto il codice della test-suite parziale da verificare
					
				result_path: str
					Una stringa contenente la path, relativa alla Full Project Root Path nel container, del file
					JSON in cui verrà scritto il risultato della verifica, a livello di linting, effettuata.
		"""
		self._full_root: str = full_root
		self._ptsuite_path: str = ptsuite_path
		self._result_path: str = result_path
		
		self._pyl_reporter: ErrorCollectorPylReporter = ErrorCollectorPylReporter()
		self._error_found: LintingRelatedProblem = None
		
		self._object_used: bool = False


	def check_lintically(
			self,
			pyl_args: List[str]=None
	):
		"""
			Esegue la verifica a livello di linting della test-suite parziale associata
			raccogliendo il primo errore che si è verificato.
			
			Parameters
			----------
				pyl_args: List[str]
					Opzionale. Default = `None`. Una lista di stringhe che contine gli argomenti aggiuntivi
					da fornire al comando di `pylint` per effettuare la verifica a livello di linting
					
			Raises
			------
				LintingCheckerAlreadyUsedError
					Se questo PartialTsuite1TimeLintingChecker ha già eseguito una verifica
					a livello di linting
		"""
		if self._object_used:
			raise LintingCheckerAlreadyUsedError()
		
		if pyl_args is None:
			pyl_args = []
		
		self._pyl_reporter.init_reporter()
		
		pyl_allargs: List[str] = (
			[f"--source-roots={self._full_root}"] +
			pyl_args +
			[self._ptsuite_path]
		)
		
		PylRunner(
			pyl_allargs,
			reporter=self._pyl_reporter,
			exit=False
		)
		
		if self._pyl_reporter.has_found_any_problem():
			self._error_found = self._pyl_reporter.get_found_problems()
		else:
			self._error_found = None
			
		self._object_used = True


	def serialize_result(self):
		"""
			Serializza il primo errore trovato nella verifica a livello di linting effettuata.
			
			Il file JSON risultante dalla serializzazione contiene un dizionario, che, solo nel caso si sia
			verificato un errore di linting, è composto i seguenti campi:
			
				- "except_name": Una stringa contenente il nome dell' eccezione
				- "except_mess": Una stringa contenente il messaggio dell' eccezione
				- "except_pos": Una stringa nel formato `"row;col"` contenente la posizione nel codice dell' errore

			Raises
			------
				LintingNotExecutedError
					Si verifica se non è mai stata eseguita una verifica di linting prima di chiamare
					quest' operazione
		"""
		if not self._object_used:
			raise LintingNotExecutedError()
		
		json_enc: JSONEncoder = JSONEncoder()
		result: Dict[str, str] = dict()
		
		if self._error_found is not None:
			result["except_name"] = self._error_found.get_short_name()
			result["except_mess"] = self._error_found.get_message()
			
			error_position: Tuple[int, int] = self._error_found.get_code_position()
			result["except_pos"] = f"{str(error_position[0])};{str(error_position[1])}"
			
		with open(self._result_path, "w") as fres:
			fres.write(json_enc.encode(result))
			fres.flush()