from typing import Tuple, List

from pylint.reporters import BaseReporter
from pylint.message.message import (
	Message as LintingMessage
)



class LintingRelatedProblem:
	"""
		Rappresenta un problema (errore) identificato durante l'esecuzione
		della fase di "linting" del codice di una test suite parziale
	"""

	def __init__(self, short_name: str, message: str, line_num: int, col_num: int):
		"""
			Crea un nuovo LintingRelatedProblem

			Parameters
			----------
				short_name: str
					Il nome "corto", o per meglio dire "simbolico", dell' errore verificatosi

				message: str
					Il messaggio associato all' errore verificatosi

				line_num: str
					Il numero della linea in cui si è verificato l'errore

				col_num: str
					Il numero della colonna in cui si è verificato l' errore
		"""
		self._short_name: str = short_name
		self._message: str = message
		self._line_num: int = line_num
		self._col_num: int = col_num


	def get_short_name(self) -> str:
		return self._short_name


	def get_message(self) -> str:
		return self._message


	def get_code_position(self) -> Tuple[int, int]:
		"""
			Returns
			-------
			Tuple[int, int]
				Una tupla di interi contenente:

					* [0]: Il numero di riga in cui si è verificato l' errore
					* [1]: Il numero di colonna in cui si è verificato l' errore
		"""
		return (self._line_num, self._col_num)


	"""
		Formato:
		
		<short_name>: <message> (at line <line_num>, at column <col_num>)
	"""
	def build_formatted_message(self) -> str:
		"""
			TODO: Contratto

			Returns
			-------
			str
		"""
		return f"{self._short_name}: {self._message} (occurred at line {self._line_num}, at column {self._col_num})"


class ErrorCollectorPylReporter(BaseReporter):
	"""
		Rappresenta un reporter personalizzato di PyLint in grado di registrare
		tutte le failures che si verificano durante il linting di un modulo dato
		come argomento al Callable `Run(...)`

		Come tutti i reporters di PyLint è da utilizzarsi instanziandone un
		oggetto, e passando quest' ultimo come argomento al Callable `Run(...)`
		(precisamente all' argomento `reporter`).
	"""

	CAPTURED_MESSAGES = frozenset([
		"error",
		"fatal"
	])

	def __init__(self):
		"""
			Crea un nuovo ErrorCollectorPylReporter

			Questo reporter di PyLint, prima di essere utilizzato, in ogni nuova `Run` di PyLint,
			va inizializzato tramite il metodo `init_reporter()`
		"""
		super().__init__()

		self._captured_errors: List[LintingRelatedProblem] = None
		self._idle: bool = False
		self._has_found_errors: bool = False


	# ======================== Hooks per PyLint ================================
	def handle_message(self, msg: LintingMessage):
		if not self._idle:
			raise RuntimeError("The reporter object has not been initialized with method " +
							   "`init_reporter` before this pylint run")

		if msg.category in ErrorCollectorPylReporter.CAPTURED_MESSAGES:
			self._has_found_errors = True

			self._captured_errors.append(
				LintingRelatedProblem(
					msg.symbol,
					msg.msg,
					msg.line,
					msg.column
				)
			)

	def display_messages(self, layout):
		# Deve essere implementato
		# Viene eseguito sempre alla fine della fase di linting
		self._idle = False


	def display_reports(self, layout):
		# Non necessario, ma deve essere implementato
		pass


	def _display(self, layout):
		# Metodo richiesto ma può essere lasciato vuoto
		pass
	# ==========================================================================


	def init_reporter(self):
		"""
			TODO: Contratto

			Returns
			-------

		"""
		del self._captured_errors
		self._captured_errors = list()
		self._has_found_errors = False

		self._idle = True


	def has_found_any_problem(self) -> bool:
		"""
			TODO: Contratto

			Returns
			-------

		"""
		return self._has_found_errors


	def get_found_problems(self) -> List[LintingRelatedProblem]:
		"""
			TODO: Contratto

			Returns
			-------

		"""
		return self._captured_errors