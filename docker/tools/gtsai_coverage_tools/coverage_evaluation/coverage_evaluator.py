from typing import List, Dict

from subprocess import run as subp_run

from .e_cov_reporttype import ECoverageReportType

from .exceptions import (
	CoverageNotEvaluatedError, ReportNotProcessedError
)



class CoverageEvaluator:
	"""
		Rappresenta un valutatore della coverage, tramite coverage.py, di un gruppo di test-suites fornito
		rispetto al suo specifico codice focale
	"""
	
	_REPORT_CMDS: Dict[ECoverageReportType, str] = {
		ECoverageReportType.HTML: "html",
		ECoverageReportType.JSON: "json",
		ECoverageReportType.XML: "xml",
		ECoverageReportType.LCOV: "lcov",
		ECoverageReportType.ANNOTATE: "annotate",
	}
	
	def __init__(
			self,
			rcfile_path: str,
			report_type: ECoverageReportType = ECoverageReportType.JSON,
			test_runner_pgm: str= "pytest"
	):
		"""
			Costruisce un nuovo CoverageEvaluator che produce reports del tipo selezionato
			
			Parameters
			----------
				rcfile_path: str
					Una stringa contenente la path del file "coverage.rc" da utilizzare come
					opzioni per il calcolo della coverage
					
				report_type: ECoverageReportType
					Un valore `ECoverageReportType` che indica il tipo di report che verrà
					prodotto dalla valutazione effettuata
					
				test_runner_pgm: str
					Opzionale. Default = `pytest`. Una stringa contenente il nome del comando esecutore
					dei tests a cui si aggancerà coverage.py
		"""
		if (rcfile_path is None) or (rcfile_path == ""):
			raise ValueError()
		
		self._evaluated: bool = False
		self._processed: bool = False
		
		self._rcfile_path: str = rcfile_path
		self._report_type: str = self._REPORT_CMDS[report_type]
		self._tester_pgm: str = test_runner_pgm
		
		self._glob_args: Dict[str, str] = dict()
		self._run_args: Dict[str, str] = dict()
		self._tester_args: Dict[str, str] = dict()
		
		self._tests_root: str = None


	def set_covpy_args(
			self,
	        general_args: Dict[str, str]=None,
			runop_args: Dict[str, str]=None
	):
		"""
			Imposta gli argomenti della chiamata a coverage.py da linea di comando
			
			Parameters
			----------
				general_args: Dict[str, str]
					Opzionale. Default = `None`. Un dizionario di stringhe, indicizzato da stringhe
					contenente gli argomenti da passare all' esecuzione dell' intero
					software coverage.py
					
				runop_args: Dict[str, str]
					Opzionale. Default = `None`. Un dizionario di stringhe, indicizzato da stringhe
					contenente gli argomenti da passare all' esecuzione dell' operazione "run"
					del software coverage.py
					
			Raises
			------
				ValueError
					Si verifica se:
					
						- Almeno uno tra il parametro `general_args` e `runop_args` sono dizionari vuoti
						- Almeno uno tra il parametro `general_args` o `runop_args` contengono una entry con valore `None`
						- Il parametro `runop_args` contiene una entry con chiave "--rcfile"
		"""
		if (len(general_args) == 0) or (len(runop_args) == 0):
			raise ValueError()
		if general_args is not None:
			for key, value in general_args.items():
				if value is None:
					raise ValueError()
		if runop_args is not None:
			for key, value in runop_args.items():
				if (key == "--rcfile") or (value is None):
					raise ValueError()
		
		if general_args is not None:
			self._glob_args = general_args
		else:
			del self._glob_args
			self._glob_args = dict()
		
		if runop_args is not None:
			self._run_args = runop_args
		else:
			del self._run_args
			self._run_args = dict()


	def set_tester_args(self, args: Dict[str, str]=None):
		"""
			Imposta gli argomenti della chiamata, a linea di comando, dell' esecutore dei tests selezionato
			
			Parameters
			----------
				args: Dict[str, str]
					Opzionale. Default = `None`. Un dizionario di stringhe, indicizzato da stringhe
					contenente gli argomenti da passare all' esecutore dei tests selezionato
					
			Raises
			------
				ValueError
					Si verifica se il parametro `args` è un dizionario vuoto
		"""
		if len(args) == 0:
			raise ValueError()
		
		if args is not None:
			self._tester_args = args
		else:
			del self._tester_args
			self._tester_args = dict()


	def evaluate(
			self,
			tests_root: str
	):
		"""
			Esegue il calcolo della coverage sulla root path dei tests specfici 
			
			Parameters
			----------
				tests_root: str
					Una stringa rappresentante la root path dei tests di cui calcolare
					la coverage
					
			Raises
			------
				ValueError
					Si verifica se il parametro `tests_root` ha valore `None`
					o è una stringa vuota
		"""
		whole_cmd: List[str] = ["coverage"]
		
		for flag, value in self._glob_args.items():
			whole_cmd.append(flag)
			if (value is not None) and (value != ""):
				whole_cmd.append(value)
		
		whole_cmd.extend(["run", f"--rcfile={self._rcfile_path}"])
		
		for flag, value in self._run_args.items():
			whole_cmd.append(flag)
			if (value is not None) and (value != ""):
				whole_cmd.append(value)
		
		whole_cmd.append("-m")
		whole_cmd.append(self._tester_pgm)
		
		for flag, value in self._tester_args.items():
			whole_cmd.append(flag)
			if (value is not None) and (value != ""):
				whole_cmd.append(value)
			
		whole_cmd.append(tests_root)
		
		subp_run(whole_cmd)
		
		self._evaluated = True


	def process_report(self):
		"""
			Prepara un report, indipendentemente dalla tipologia che verrà scelta,
			sul calcolo della coverage che è stato effettuato precedentemente alla chiamata
			di quest' operazione
		"""
		if not self._evaluated:
			raise CoverageNotEvaluatedError()
		
		subp_run(["coverage", "report", f"--rcfile={self._rcfile_path}"])
		
		self._processed = True
	
	
	def create_report(self):
		"""
			Crea il report di coverage della tipologia selezionata alla costruzione di questo
			CoverageEvaluator
		"""
		if not self._evaluated:
			raise CoverageNotEvaluatedError()
		if not self._processed:
			raise ReportNotProcessedError()
		
		subp_run(["coverage", self._report_type])
		
		self._evaluated = False
		self._processed = False


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================