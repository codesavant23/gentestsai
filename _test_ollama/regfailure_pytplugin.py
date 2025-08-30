from typing import Dict, List, Any
from pytest import (
	hookimpl as pyt_hookimpl,
	TestReport as PytTestReport
)


class RegisterFailurePyTestPlugin:
	"""
		Rappresenta un plugin personalizzato di PyTest in grado di registrare
		la prima failure che si verifica durante un' esecuzione di `pytest.main`
		registrando l' errore verificatosi e il suo messaggio associato.

		Come tutti i plugins di PyTest è da utilizzarsi instanziandone un
		oggetto, e passando quest' ultimo come argomento a una chiamata
		di `pytest.main(...)` (precisamente all' iteratore dell' argomento `plugin`).
	"""

	def __init__(self):
		"""
			Crea un nuovo FailureExceptPyTestPlugin
		"""
		self._plugin_ready: bool = False

		self._error: Dict[str, str] = None
		self._import_error: bool = False


	"""
		Non ImportError ---> "tests/test_example.py::test_fail" 
		oppure
		ImportError ---> "tests/test_bad_import.py"

		In ogni caso, gli altri:
			- <nome_eccezione>
			- <messaggio_eccezione>
	"""
	def _register_failure(self,
		who_failed: str,
		except_name: str,
		except_message: str,
	):
		who_failed_parts: List[str] = who_failed.strip().split("::")
		file_failed: str = who_failed_parts[0]
		test_failed: str = ""
		if len(who_failed_parts) > 1:
			test_failed = who_failed_parts[1]

		self._error = {
			"who_failed": (file_failed, test_failed),
			"except_name": except_name,
			"except_message": except_message,
		}


	# Con questo hook si intercettano gli errori di importing o di raccolta test
	@pyt_hookimpl(hookwrapper=True)
	def pytest_collectreport(self, report):
		outcome = yield

		if self._plugin_ready:
			exec_result: PytTestReport = outcome.get_result()

			if exec_result.failed and self._error is None:
				exception = getattr(exec_result.longrepr.getrepr().reprcrash, "message", str(exec_result.longrepr))
				exception_parts = exception.split(":")

				self._import_error = True
				self._register_failure(
					who_failed=getattr(exec_result, "nodeid", getattr(exec_result, "nodeid", "collect_error")),
					except_name=exception_parts[0],
					except_message=exception_parts[1]
				)


	# Con questo hook si considerano tutte le fasi successive: Setup dei tests, Call dei tests e Teardown dei Tests
	@pyt_hookimpl(hookwrapper=True)
	def pytest_runtest_makereport(self, item, call):
		outcome = yield

		if self._plugin_ready:
			exec_result: PytTestReport = outcome.get_result()

			if exec_result.failed and self._error is None:
				exception = getattr(exec_result.longrepr.getrepr().reprcrash, "message", str(exec_result.longrepr))
				exception_parts = exception.split(":")

				self._import_error = False
				self._register_failure(
					who_failed=getattr(exec_result, "nodeid", "unknown"),
					except_name=exception_parts[0],
					except_message=exception_parts[1]
				)


	# Con questo hook si va a gestire la fase finale: post-esecuzione (di successo, o fallimentare) di tutti i tests
	@pyt_hookimpl(hookwrapper=True)
	def pytest_unconfigure(self, config):
		yield

		self._plugin_ready = False


	def init_plugin(self):
		"""
			Inizializza questo plugin per una nuova esecuzione di PyTest (`pytest.main(...)`)
		"""
		del self._error
		self._error = None
		self._import_error = False

		self._plugin_ready = True


	def has_run_failed(self) -> bool:
		"""
			Permette di comprendere se l' ultima esecuzione di PyTest, a cui
			questo plugin è stato associato, è fallita generando un errore

			Returns
			-------
			bool
				Un booleano che assume valore:
					* `True`: Se l' ultima esecuzione a cui questo plugin è stato associato ha generato un errore
					* `False`: Se l' ultima esecuzione a cui questo plugin è stato associato ha generato un errore
		"""
		if not (self._error is None):
			return True
		else:
			return False


	def is_import_error(self) -> bool:
		"""
			Indica se un errore, nel caso in cui si sia verificato, sia relativo alla fase di
			calcolo degli imports.

			ASSUNZIONE: Nel caso in cui l' errore non si sia verificato questo metodo restituisce
			sempre un booleano `False`

			Returns
			-------
			bool
				Un booleano indicante se l' errore è relativo ad un errore di importing
		"""
		if self.has_run_failed():
			return self._import_error
		else:
			return False


	def get_error_info(self) -> Dict[str, str]:
		"""
			Restituisce una eventuale failure verificatasi durante l' esecuzione della chiamata
			a `pytest.main(...)` a cui questo plugin è stato associato.

			Se non è stato riscontrato alcun errore restituisce None.

			Returns
			-------
			Dict[str, str]
				Un dizionario, indicizzato su stringhe, contenente:
					* "who_failed": Una tupla di stringhe contenente:

						* [0]: La path del file che ha generato l'errore
						* [1]: Il nome del test che ha generato l'errore se questo non deriva da un importing

					* "except_name": Il nome dell' errore generatosi
					* "except_message": Il messaggio dell' errore generatosi
				Oppure None se non è stato riscontrato alcun errore
		"""
		return self._error