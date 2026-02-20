from typing import Tuple
from abc import abstractmethod
from ._a_base_syntcker import _ABaseSyntacticChecker

from datetime import datetime as DateTime
from py_compile import (
	compile as py_compile,
	PycInvalidationMode as Pyc_InvMode,
	PyCompileError
)
# ============ Path Utilities ============ #
from os.path import join as path_join
# ======================================== #
# ============== OS Utilities ============== #
from os import makedirs as os_mkdirs
from shutil import rmtree as os_dremove
from tempfile import gettempdir as os_tempdir
# ========================================== #
# ============= RegEx Utilities ============ #
from regex import search as reg_search
# ========================================== #



class PyCompileSyntChecker(_ABaseSyntacticChecker):
	"""
		Rappresenta un `ISyntChecker` che utilizza il tool di verifica
		`pycompile`.
	"""
	
	_PYCOMP_EXCNAME_PATT: str = r"[A-Z][\w_\-]+Error"
	
	def __init__(self):
		"""
			Costruisce un nuovo PyCompileSyntChecker
		"""
		timestamp: str = str(int(DateTime.now().timestamp() * 1000))
		temp_fname: str = f"temp_{timestamp}.py"
		self._TEMP_BASEPATH: str = path_join(
			os_tempdir(),
			"gentests_ai",
			"correction",
			"synt"
		)
		
		os_dremove(self._TEMP_BASEPATH, ignore_errors=False)
		os_mkdirs(self._TEMP_BASEPATH)
		self._inited: bool = True
		
		self._tempfile_path: str = path_join(
			self._TEMP_BASEPATH,
			temp_fname
		)
		
		
	def _ap__check_synt_spec(self, ptsuite_code: str) -> Tuple[str, str]:
		self._write_on_tempfile(ptsuite_code)
		
		try:
			py_compile(
				self._tempfile_path,
				doraise=True,
				invalidation_mode=Pyc_InvMode.TIMESTAMP
			)
			return tuple()
		except PyCompileError as synt_error:
			except_name: str = reg_search(self._PYCOMP_EXCNAME_PATT, synt_error.exc_type_name).group()
			except_mess: str = synt_error.args[0]
			return (except_name, except_mess)
	
	
	def clear_resources(self):
		"""
			Ripulisce le risorse che sono state utilizzate dal verificatore
			a livello di linting
		"""
		os_dremove(self._TEMP_BASEPATH, ignore_errors=False)
		self._inited = False
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	def _write_on_tempfile(self, ptsuite_code: str):
		"""
			Scrive la test-suite parziale data sul file temporaneo
			per la verifica di correttezza sintattica
			
			Parameters
			----------
				ptsuite_code: str
					Una stringa contenente il codice della test-suite parziale di cui
					effettuare la verifica di correttezza sintattica
		"""
		if not self._inited:
			os_dremove(self._TEMP_BASEPATH, ignore_errors=False)
			os_mkdirs(self._TEMP_BASEPATH)
			self._inited = True
		
		with open(self._tempfile_path, "w") as fptsuite:
			fptsuite.write(ptsuite_code)
			fptsuite.flush()