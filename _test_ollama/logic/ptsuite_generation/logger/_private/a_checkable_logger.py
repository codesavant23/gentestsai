from typing import TextIO, Dict, Set
from abc import abstractmethod

from logic.ptsuite_generation.logger import AFormattableLogger

from logic.ptsuite_generation.logger.exceptions import NotWritableStreamError



class ACheckableLogger(AFormattableLogger):
	"""
		Rappresenta un `ILogger` che ha la capacità di verificare il tipo di stream
		di output che viene fornito
		
		Il tipo di stream di output è specificato dai discendenti di questa classe astratta.
		I placeholders del formato sono specificati dai discendenti di questa classe astratta.
	"""
	
	def __init__(
			self,
			stream: TextIO
	):
		"""
			Costruisce un nuovo ACheckableLogger fornendo lo stream di output
			da verificare prima di associarlo a questo logger
			
			Parameters
			----------
				stream: TextIO
					Un oggetto `TextIO` rappresentante lo stream di output da verificare
			
			Raises
			------
				NotWritableStreamError
					Si verifica se lo stream fornito:
					
						- Lo stream fornito non è uno di output
						- Lo stream fornito è chiuso
			
				InvalidStreamTypeError
					Si verifica se lo stream fornito è di un tipo invalido rispetto al tipo di stream
					specificato dai discendenti di questa classe astratta
		"""
		super().__init__()
		
		if (not stream.writable()) or stream.closed:
			raise NotWritableStreamError()
		
		self._ap__assert_stream_type(stream)
		
		self._stream: TextIO = stream
	
	
	def _ap__write_log(self, log_message: str):
		self._stream.write(log_message)
		self._stream.flush()
	
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	
	
	@abstractmethod
	def _ap__assert_format(self, placehs: Set[str]):
		pass


	@abstractmethod
	def _ap__format_vars(self) -> Dict[str, str]:
		pass


	@abstractmethod
	def _ap__assert_stream_type(
			self,
			stream: TextIO
	):
		"""
			Verifica che lo stream di output fornito rispetti il tipo di stream di output
			specificato dai discendenti di questa classe astratta.

			Se la verifica ha successo quest' operazione è equivalente ad una no-op
			
			Parameters
			----------
				stream: TextIO
					Un oggetto `TextIO` rappresentante lo stream di output da verificare
					
			Raises
			------
				InvalidStreamTypeError
					Si verifica se lo stream fornito è di un tipo invalido rispetto al tipo di stream
					specificato dai discendenti di questa classe astratta
		"""
		pass