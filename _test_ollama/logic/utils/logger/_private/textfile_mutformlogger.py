from typing import List, TextIO
from .. import ATemporalFormattLogger

from ..exceptions import InvalidStreamTypeError



class TextFileMutableFormattableLogger(ATemporalFormattLogger):
	"""
		Rappresenta `ATemporalFormattLogger` che registra messaggi su un file testuale.
	"""
	
	def __init__(
			self,
	        stream: TextIO
	):
		"""
			Costruisce un nuovo TextFileMutableLogger
			
			Parameters
			----------
				stream: TextIO
					Un oggetto `TextIO` rappresentante lo stream di output da verificare
					
			Raises
			------
				NotWritableStreamError
					Si verifica se lo stream fornito non è scrivibile (e quindi di output)
					
				InvalidStreamTypeError
					Si verifica se lo stream fornito è di un tipo invalido rispetto al tipo di stream
					specificato dai discendenti di questa classe astratta
		"""
		super().__init__(stream)
	
	
	def _ap__assert_stream_type(self, stream: TextIO):
		parts: List[str] = stream.name.split(".")
		if len(parts) > 1:
			if parts[1] != "txt":
				raise InvalidStreamTypeError()