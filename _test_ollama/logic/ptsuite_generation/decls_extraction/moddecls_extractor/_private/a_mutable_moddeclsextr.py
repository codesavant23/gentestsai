from typing import List
from abc import abstractmethod
from .. import IModuleDeclsExtractor

# ============== OS Utilities ============== #
from os import remove as os_remove
from tempfile import gettempdir as os_tempdir
# ========================================== #
# ============ Path Utilities ============ #
from pathlib import Path as SystemPath
# ======================================== #
from datetime import datetime as DateTime
from py_compile import (
	compile as py_compile,
	PycInvalidationMode as Pyc_InvMode,
	PyCompileError
)

from ...classdecls_extractor import IClassDeclsExtractor

from ..exceptions import IncorrectModuleCodeError



class AMutableModuleDeclsExtractor(IModuleDeclsExtractor):
	"""
		Rappresenta un `IModuleDeclsExtractor` a cui è possibile variare il codice del module-file associato.
		
		La tecnologia implementativa dell' estrazione è specificata dai discendenti di questa interfaccia.
	"""
	
	def __init__(
			self,
			module_code: str
	):
		"""
			Costruisce un nuovo AMutableModuleDeclsExtractor fornendo il primo module-file
			da cui estrarne le dichiarazioni di funzioni e classi
			
			Parameters
			----------
				module_code: str
					Una stringa contenente il codice del module-file di cui estrarre
					le dichiarazioni
					
			Raises
			------
				ValueError
					Si verifica se:
					
						- La stringa fornita è vuota
						- E' stato fornito `None` come valore di `module_code`
						
				IncorrectModuleCodeError
					Si verifica se il codice del modulo contiene errori da un punto di vista sintattico
		"""
		self._module_code: str = None
		self.set_module_code(module_code)


	def set_module_code(
			self,
	        module_code: str
	):
		"""
			Imposta il codice del prossimo module-file di cui estrarne le eventuali
			funzioni e/o le eventuali classi

			Parameters
			----------
				module_code: str
					Una stringa contenente il codice del module-file di cui estrarre, e
					separare, eventuali funzioni e/o eventuali classi
					
			Raises
			------
				ValueError
					Si verifica se:
					
						- La stringa fornita è vuota
						- E' stato fornito `None` come valore di `module_code`
						
				IncorrectModuleCodeError
					Si verifica se il codice del modulo contiene errori da un punto di vista sintattico
		"""
		if module_code is None:
			raise ValueError()
		if module_code == "":
			raise ValueError()
		self._assert_synt_correctness(module_code)
		
		self._module_code = module_code
		
	
	#	============================================================
	#						ABSTRACT METHODS
	#	============================================================


	@abstractmethod
	def extract_funcs(self) -> List[str]:
		pass
	
	
	@abstractmethod
	def extract_classes(self) -> List[IClassDeclsExtractor]:
		pass
	
	
	#	============================================================
	#						PRIVATE METHODS
	#	============================================================
	
	
	def _pf_get_module_code(self) -> str:
		"""
			Restituisce il codice dell' ultimo module-file code impostato
			
			Returns
			-------
				str
					Una stringa contenente il codice dell' ultimo module-file
					Python impostato
		"""
		return self._module_code
	
	
	@classmethod
	def _assert_synt_correctness(
			cls,
			module_code: str
	):
		"""
			Verifica se il codice del module-file dato è corretto sintatticamente
			
			Parameters
			----------
				module_code: str
					Una stringa contenente il codice del module-file di cui verificare
					la correttezza sintattica
					
			Raises
			------
				IncorrectModuleCodeError
					Si verifica se il codice del modulo contiene errori da un punto di vista sintattico
		"""
		now: DateTime = DateTime.now()
		tmpfile_name: str = (
				"tmp_" +
				f"{int(now.timestamp()*100)}" +
				".py"
		)
		tmpfile_path: SystemPath = SystemPath(os_tempdir(), tmpfile_name)
		
		with tmpfile_path.open("w") as ftemp:
			ftemp.write(module_code)
			ftemp.flush()
			
		try:
			py_compile(
				str(tmpfile_path),
				doraise=True,
				invalidation_mode=Pyc_InvMode.TIMESTAMP
			)
		except PyCompileError as err:
			os_remove(str(tmpfile_path))
			raise IncorrectModuleCodeError()
		
		os_remove(str(tmpfile_path))