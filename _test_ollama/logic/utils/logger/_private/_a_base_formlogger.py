from typing import Set, Dict, TextIO
from abc import abstractmethod
from .. import IFormattableLogger

from string import Formatter as StrFormatter

from ..exceptions import (
	NotWritableStreamError,
	FormatNotSetError
)



class _ABaseFormattableLogger(IFormattableLogger):
	"""
		Rappresenta un `IFormattableLogger` di base, ovvero che contiene la logica
		di controllo comune ad ogni `IFormattableLogger`.
		
		Il tipo di stream di output è specificato dai discendenti di questa classe astratta.
		Altri placeholders del formato sono specificati dai discendenti di questa classe astratta.
	"""
	
	def __init__(
			self,
			stream: TextIO
	):
		"""
			Costruisce un nuovo AFormattableLogger fornendo lo stream di output
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
		if (not stream.writable()) or stream.closed:
			raise NotWritableStreamError()
		
		self._ap__assert_stream_type(stream)
		
		self._stream: TextIO = stream
		
		self._format: str = None
		self._parser: StrFormatter = StrFormatter()
		
		self._sep: str = None


	def set_format(
			self,
			format_str: str
	):
		if (format_str is None):
			raise ValueError()
		
		placehs: Set[str] = {
		    placeh
		    for _, placeh, _, _ in self._parser.parse(format_str)
		    if placeh is not None
		}
		placehs = placehs.difference({"message"})
		self._ap__assert_format(placehs)
		
		self._format = format_str
	
	
	def unset_format(self) -> str:
		if self._format is None:
			raise FormatNotSetError()
		
		old_format: str = self._format
		self._format = None
		return old_format
	
	
	def set_messages_sep(self, new_sep: str):
		if (self._sep is None):
			raise ValueError()
		
		self._sep = new_sep
	
	
	def log(
			self,
			message: str
	):
		"""
			Registra un nuovo messaggio sullo stream di output fornito, formattandolo prima della
			scrittura se è stato impostato un formato
			
			Parameters
			----------
				message: str
					Una stringa contenente il messaggio da registrare sullo stream di output
		"""
		log_message: str = message
		if self._format is not None:
			format_vars: Dict[str, str] = self._ap__format_vars()
			format_vars["message"] = message
			log_message = str.format_map(self._format, format_vars)
			
		self._stream.write(log_message + self._sep)
		self._stream.flush()
		
		
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	
	
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
	
	
	@abstractmethod
	def _ap__format_vars(self) -> Dict[str, str]:
		"""
			Restituisce i placeholders di formattazione specificati dai discendenti di questa
			classe astratta e i loro valori associati
			
			Returns
			-------
				Dict[str, str]
					Un dizionario di stringhe, indicizzato da stringhe, contenente:
						- Come chiavi: I placeholders del formato specificato dai discendenti
						- Come valori: I valori di quei placeholders
		"""
		pass
	
	
	@abstractmethod
	def _ap__assert_format(self, placehs: Set[str]):
		"""
			Verifica che i placeholders di un formato fornito siano coerenti
			con quelli specificati dai discendenti di questa classe astratta.
			
			Se la verifica ha successo quest' operazione è equivalente ad una no-op
			
			Parameters
			----------
				placehs: Set[str]
					Un insieme di stringhe contenente i placeholders di un nuovo formato
					da impostare
					
			Raises
			------
				InvalidFormatError
					Si verifica se è stato fornito un formato con placeholders differenti
					da quelli accettabili dai discendenti di questa classe astratta
		"""
		pass
	
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================