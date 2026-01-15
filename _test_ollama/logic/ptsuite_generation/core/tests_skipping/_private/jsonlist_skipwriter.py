from typing import List, Any
from ._a_base_skipwriter import _ABaseSkipWriter

# ============== JSON Utilities ============== #
from json import (
	JSONEncoder,
	JSONDecoder, JSONDecodeError
)
# ============================================ #

from ..exceptions import InvalidSkippedTestsFileError



class JsonListSkipWriter(_ABaseSkipWriter):
	"""
		Rappresenta un `ISkipWriter` capace di scrivere su un file di tipo JSON.
		
		Il formato del file JSON è il seguente:
			
			[
				"skipped_entity1",
				"skipped_entity2",
				...
			]
	"""
	
	def __init__(
			self,
			skipdtests_path: str
	):
		"""
			Costruisce un nuovo JsonListSkipWriter
			
			Parameters
			----------
				skipdtests_path: str
					Una stringa rappresentante la path che contiene, o conterrà,
					il file dei tests saltati da utilizzare
					
			Raises
			------
				ValueError
					Si verifica se:
						
						- Il parametro `skipdtests_path` ha valore `None`
						- Il parametro `skipdtests_path` è una stringa vuota
		"""
		super().__init__(skipdtests_path)
		
		self._json_enc: JSONEncoder = JSONEncoder()
		self._json_dec: JSONDecoder = JSONDecoder()
		
		
	def write_skipd_test(
			self,
			entity_name: str
	):
		if entity_name == "":
			raise ValueError()
		
		content: List[str]
		with open(self._pf__get_skipdf_path(), "r+") as fjson:
			content = self._json_dec.decode(fjson.read())
			content.append(entity_name)
			self._json_enc.encode(content)
	
	
	#	============================================================
	#						PRIVATE METHODS
	#	============================================================


	def _p__file_extension(self) -> str:
		return "json"


	def _ap__init_skipdtests_file(
			self,
			skipdtests_path: str
	):
		with open(skipdtests_path, "r+") as fjson:
			fjson.write("[]")
			fjson.flush()
	
	
	def _ap__assert_skipdtests_file(
			self,
			skipdtests_path: str
	):
		content: str
		with open(self._pf__get_skipdf_path(), "r+") as fjson:
			content = fjson.read()
		
		content_obj: Any
		try:
			content_obj = self._json_dec.decode(content)
		except JSONDecodeError:
			raise InvalidSkippedTestsFileError()
		
		if not isinstance(content_obj, list):
			raise InvalidSkippedTestsFileError()