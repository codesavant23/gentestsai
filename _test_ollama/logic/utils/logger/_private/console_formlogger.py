from typing import TextIO, Literal
from .. import ATemporalFormattLogger

from ..exceptions import InvalidStreamTypeError



class ConsoleTemporalFormattLogger(ATemporalFormattLogger):
	"""
		Rappresenta un `ATemporalFormattLogger` che ha la capacità di scrivere su Console
		(`stdout` e `stderr`)
	"""
	
	def __init__(
			self,
	        stream: TextIO,
	):
		"""
			Costruisce un nuovo ConsoleTemporalFormattLogger fornendo lo stream di output
			da associare
			
			Parameters
			----------
				stream: TextIO
					Un oggetto `TextIO` rappresentante lo stream di output da associare
			
			Raises
			------
				NotWritableStreamError
					Si verifica se lo stream fornito non è scrivibile (e quindi di output)
			
				InvalidStreamTypeError
					Si verifica se lo stream fornito non è `stdout` o `stderr`
		"""
		super().__init__(stream)
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================
	
	
	def _ap__assert_stream_type(self, stream: TextIO):
		if stream.fileno() not in [1, 2]:
			raise InvalidStreamTypeError()