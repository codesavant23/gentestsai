from typing import TextIO, Set, Dict
from abc import abstractmethod
from .. import AMutableFormattableLogger

from datetime import datetime as DateTime

from ..exceptions import InvalidFormatError



class ATemporalFormattableLogger(AMutableFormattableLogger):
	"""
		Rappresenta un `AMutableFormattableLogger` che registra, insieme ai messaggi, forniti
		la data associata alla registrazione del messaggio.
		
		I placeholders del formato specifici implementati sono i seguenti:
			
			- {day}: Placeholder che viene valorizzato con il giorno del mese attuale
			- {month}: Placeholder che viene valorizzato con il numero del mese attuale
			- {year}: Placeholder che viene valorizzato con il numero dell' anno attuale
			- {hour}: Placeholder che viene valorizzato con l' ora attuale
			- {min}: Placeholder che viene valorizzato con i minuti trascorsi dall' inizio dell' ora attuale
			- {second}: Placeholder che viene valorizzato con i secondi trascorsi dall' inizio del minuto attuale
			
		Il tipo di stream di output utilizzato è specificato dai discendenti di questa classe astratta.
		Gli altri placeholders del formato sono specificati dai discendenti di questa classe astratta.
	"""
	
	_DATE_PLACEHS: Set[str] = {
		"day", "month", "year",
		"hour", "min", "second"
	}
	
	def __init__(
			self,
			stream: TextIO
	):
		"""
			Costruisce un nuovo ATemporalFormattableLogger associandolo allo stream di output
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
		# =========== PROTECTED ATTRIBUTES ===========
		# ============================================
		super().__init__(stream)
	
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	
	
	@abstractmethod
	def _ap__assert_stream_type(self, stream: TextIO):
		pass
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	def _ap__assert_format(self, placehs: Set[str]):
		extra_fields: Set[str] = (
			placehs.difference(self._DATE_PLACEHS).union(
			self._DATE_PLACEHS.difference(placehs))
		)
		if extra_fields != {}:
			raise InvalidFormatError()
		
		self._curr_placehs = placehs
	
	
	def _ap__format_vars(self) -> Dict[str, str]:
		placehs: Dict[str, str] = dict()
		if len(self._curr_placehs) == 0:
			return placehs
		
		datenow: DateTime = DateTime.now()
		if "day" in self._curr_placehs:
			placehs["day"] = str(datenow.day)
		if "month" in self._curr_placehs:
			placehs["month"] = str(datenow.month)
		if "year" in self._curr_placehs:
			placehs["year"] = str(datenow.year)
		if "hour" in self._curr_placehs:
			placehs["hour"] = str(datenow.hour)
		if "min" in self._curr_placehs:
			placehs["min"] = str(datenow.minute)
		if "second" in self._curr_placehs:
			placehs["second"] = str(datenow.minute)
			
		return placehs