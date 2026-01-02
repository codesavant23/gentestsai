from typing import TextIO

from logic.ptsuite_generation.logger import ATemporalLogger

from logic.ptsuite_generation.logger.exceptions import InvalidStreamTypeError



class ConsoleLogger(ATemporalLogger):
	"""
		Rappresenta `ACheckableLogger` che ha la capacità di scrivere su Console
		(`stdout` e `stderr`)
	"""
	
	def __init__(
			self,
	        stream: TextIO
	):
		"""
			Costruisce un nuovo ACheckableLogger fornendo lo stream di output
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