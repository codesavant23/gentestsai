from typing import Set, Dict, TextIO
from abc import abstractmethod

from . import ACheckableLogger

from .exceptions import NotWritableStreamError



class AMutableLogger(ACheckableLogger):
	"""
		Rappresenta un `ACheckableLogger` che ha la capacità di variare lo stream di output
		su cui registrare i messaggi.
		
		Il tipo di stream di output utilizzato è specificato dai discendenti di questa classe astratta.
		I placeholders del formato sono specificati dai discendenti di questa classe astratta.
	"""
	
	def __init__(
			self,
	        stream: TextIO
	):
		"""
			Costruisce un nuovo AMutableLogger associandolo allo stream di output
			fornito
			
			Parameters
			----------
				stream: TextIO
					Un oggetto `TextIO` rappresentante il primo stream di output da associare
					a questo logger
					
			Raises
			------
				NotWritableStreamError
					Si verifica se lo stream fornito non è scrivibile (e quindi di output)
			
				InvalidStreamTypeError
					Si verifica se lo stream fornito è di un tipo invalido rispetto al tipo di stream
					specificato dai discendenti di questa classe astratta
		"""
		super().__init__(stream)
		
		
	def change_stream(
			self,
			new_stream: TextIO
	):
		"""
			Cambia lo stream di output su cui registrare i messaggi del logger
			
			Parameters
			----------
				new_stream: TextIO
					Un oggetto `TextIO` rappresentante il nuovo stream di output da utilizzare
					
			Raises
			------
				NotWritableStreamError
					Si verifica se lo stream fornito non è scrivibile (e quindi di output)
			
				InvalidStreamTypeError
					Si verifica se lo stream fornito è di un tipo invalido rispetto al tipo di stream
					specificato dai discendenti di questa classe astratta
		"""
		if not new_stream.writable():
			raise NotWritableStreamError()
		
		self._ap__assert_stream_type(new_stream)
		
		self._p_stream = new_stream
		
		
	#	============================================================
	#						ABSTRACT METHODS
	#	============================================================
	
	@abstractmethod
	def _ap__assert_format(self, placehs: Set[str]):
		pass


	@abstractmethod
	def _ap__format_vars(self) -> Dict[str, str]:
		pass
	

	@abstractmethod
	def _ap__assert_stream_type(self, stream: TextIO):
		pass