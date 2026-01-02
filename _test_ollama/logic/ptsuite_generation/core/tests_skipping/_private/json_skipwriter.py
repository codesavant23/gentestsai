from typing import List
from .. import AMutableInitializableSkipWriter

# ============== JSON Utilities ============== #
from json import (
	JSONEncoder,
	JSONDecoder, JSONDecodeError
)
# ============================================ #

from ..exceptions import InvalidSkippedTestsFileError



class JsonSkipWriter(AMutableInitializableSkipWriter):
	"""
		Rappresenta un `AMutableInitializableSkipWriter` capace di scrivere su un file di tipo JSON.
		
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
			Costruisce un nuovo JsonSkipWriter
			
			Parameters
			----------
				skipdtests_path: str
					Una stringa rappresentante la path che contiene il file dei tests saltati da utilizzare
		"""
		super().__init__(skipdtests_path)
		
		self._json_enc: JSONEncoder = JSONEncoder()
		self._json_dec: JSONDecoder = JSONDecoder()
		
		
	def write_skipd_test(
			self,
			entity_name: str
	):
		"""
			Scrive sul file associato, dei tests saltati, che il test legato all' entità specificata
			non è andato a buon fine in una delle 2 fasi di generazione o correzione
			
			Parameters
			----------
				entity_name: str
					Una stringa contenente il nome dell' entità di codice autonoma (funzione o metodo)
					la cui generazione o correzione non è andata a buon fine
					
			Raises
			------
				ValueError
					Si verifica se la stringa data è vuota
						
				OSError
					Si verifica se non è possibile scrivere sul file associato
		"""
		if entity_name == "":
			raise ValueError()
		
		content: List[str]
		with open(self.get_skiptests_file(), "r+") as fjson:
			content = self._json_dec.decode(fjson.read())
			content.append(entity_name)
			self._json_enc.encode(content)


	def _ap__init_skipdtests_file(
			self,
			skipdtests_path: str
	):
		with open(skipdtests_path, "w") as fjson:
			fjson.write("[]")
	
	
	def _ap__assert_skipdtests_file(
			self,
			skipdtests_path: str
	):
		extens: str = skipdtests_path.split(".")[1].lower()
		if extens != "json":
			raise InvalidSkippedTestsFileError()
		content: str
		with open(self.get_skiptests_file(), "r+") as fjson:
			content = fjson.read()
			
		try:
			self._json_dec.decode(content)
		except JSONDecodeError:
			raise InvalidSkippedTestsFileError()