from typing import List

from pylint.reporters import BaseReporter
from pylint.message.message import (
	Message as LintingMessage
)

from . import LintingRelatedProblem

from .execeptions import (
	LintingNotExecutedError,
	ErrorCollectorNotInitializedError
)



class ErrorCollectorPylReporter(BaseReporter):
	"""
		Rappresenta un reporter personalizzato di PyLint in grado di registrare
		tutte le failures che si verificano durante il linting di un modulo dato
		come argomento al Callable `pylint.lint.Run(...)`

		Come tutti i reporters di PyLint è da utilizzarsi instanziandone un
		oggetto, e passando quest' ultimo come argomento al Callable `pylint.lint.Run(...)`
		(precisamente all' argomento `reporter`).
	"""

	CAPTURED_MESSAGES = frozenset([
		"error",
		"fatal"
	])

	def __init__(self):
		"""
			Crea un nuovo ErrorCollectorPylReporter
			
			E' necessario, dopo ciò, eseguire l' operazione `init_reporter(...)`.
			E' necessario, inoltre, ri-eseguire `init_reporter(...)` prima di riutilizzare quest' oggetto
			in ogni nuova `pylint.lint.Run(...)`
		"""
		super().__init__()

		self._captured_errors: List[LintingRelatedProblem] = None
		self._idle: bool = False
		self._runned: bool = False
		self._has_found_errors: bool = False


	# ======================== Hooks per PyLint ================================
	def handle_message(self, msg: LintingMessage):
		# Viene eseguito ogni volta che viene trovato un messaggio
		if not self._idle:
			raise ErrorCollectorNotInitializedError()

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
		self._runned = True


	def display_reports(self, layout):
		# Non necessario, ma deve essere implementato
		pass


	def _display(self, layout):
		# Non necessario, ma deve essere implementato
		pass
	# ==========================================================================


	def init_reporter(self):
		"""
			Inizializza questo ErrorCollectorPylReporter per utilizzarlo in una nuova
			`pylint.lint.Run(...)`
		"""
		self._captured_errors.clear()
		self._has_found_errors = False

		self._idle = True
		self._runned = False


	def has_found_any_problem(self) -> bool:
		"""
			Verifica se sono stati trovati errori nella `pylint.lint.Run(...)` eseguita precedentemente

			Returns
			-------
				bool
					Un booleano che indica se sono stati trovati errori durante la
					verifica, a livello di linting, del codice dato a `pylint.lint.Run(...)`

			Raises
			------
				LintingNotExecutedError
					Se non è stata eseguita una verifica a livello di linting prima di chiamare
					questa operazione
		"""
		if not self._runned:
			raise LintingNotExecutedError()
		return self._has_found_errors


	def get_found_problems(self) -> List[LintingRelatedProblem]:
		"""
			Restituisce le problematiche (errori) di linting trovate nella precedente esecuzione
			da parte di `pylint.lint.Run(...)`

			Returns
			-------
				List[LintingRelatedProblem]
					Una lista di oggetti `LintingRelatedProblem` relativi all' esecuzione della fase di linting
					da parte di `pylint.lint.Run(...)`
		"""
		return self._captured_errors