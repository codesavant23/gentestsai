from typing import Set, Dict
from abc import abstractmethod
from . import ILogger

from string import Formatter as StrFormatter

from .exceptions import FormatNotSetError



class AFormattableLogger(ILogger):
	"""
		Rappresenta un `ILogger` che ha la capacità di formattare il messaggio di logging
		che viene scritto sullo stream di output.
		
		La stringa di formato di base (ovvero specificata da questa classe astratta) definisce come:
			
			- "{message}": Il placeholder che contiene il messaggio fornito al metodo `.log(...)`
		
		Il tipo di stream di output è specificato dai discendenti di questa classe astratta.
		Gli altri placeholders del formato sono specificati dai discendenti di questa classe astratta.
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo AFormattableLogger
		"""
		self._format: str = None
		self._parser: StrFormatter = StrFormatter()


	def set_format(
			self,
			format_str: str
	):
		if (format_str is None) or (format_str == ""):
			raise ValueError()
		
		placehs: Set[str] = {
		    placeh
		    for _, placeh, _, _ in self._parser.parse(format_str)
		    if placeh is not None
		}
		placehs = placehs.difference({"message"})
		self._ap__assert_format(placehs)
		
		self._format = format_str
	
	
	def unset_format(self):
		if self._format is None:
			raise FormatNotSetError()
		
		self._format = None
	
	
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
			
		self._ap__write_log(log_message)
		
		
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	
	
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
	
	
	@abstractmethod
	def _ap__write_log(self, log_message: str):
		"""
			Scrive sullo stream di output il messaggio, opzionalmente formattato
			
			Parameters
			----------
				log_message: str
					Una stringa contenente il messaggio di log da scrivere sullo stream di output
		"""
		pass
	
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================