from .. import (
	ISkipWriter,
	ESkippedTestsFtypeFormat
)
from .._private._a_base_skipwriter import _ABaseSkipWriter
from .._private.jsonlist_skipwriter import JsonListSkipWriter



class SkipWriterFactory:
	"""
		Rappresenta una factory per ogni `ISkipWriter`
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo SkipWriterFactory
		"""
		pass
		
		
	def create(
			self, 
			file_type: ESkippedTestsFtypeFormat, 
			skipdtests_path: str
	) -> ISkipWriter:
		"""
			Istanzia un nuovo scrittore di tests saltati del tipo e formato specificato
			
			Parameters
			----------
				file_type: ESkippedTestsFtypeFormat
					Un valore `ESkippedTestsFtypeFormat` rappresentante il tipo e formato richiesti
					per l' oggetto `ISkipWriter`
					
				skipdtests_path: str
					Una stringa rappresentante la path che contiene, o conterrà,
					il file dei tests saltati da utilizzare
					
			Returns
			-------
				ISkipWriter
					Un oggetto `ISkipWriter` che permette la scrittura dei tests saltati
					nel tipo e formato specificati
					
			Raises
			------
				ValueError
					Si verifica se:
						
						- Il parametro `skipdtests_path` ha valore `None`
						- Il parametro `skipdtests_path` è una stringa vuota
			
				InvalidSkippedTestsFileError
					Si verifica se il file è invalido per tipo o formato
		"""
		obj: _ABaseSkipWriter
		if file_type == ESkippedTestsFtypeFormat.JSON_LIST:
			obj = JsonListSkipWriter(skipdtests_path)
		
		obj._P__objinit()
		return obj
	
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================