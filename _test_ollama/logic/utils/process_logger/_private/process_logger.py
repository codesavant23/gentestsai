from logic.utils.logger import ATemporalFormattLogger



class ProcessLogger:
	"""
		Rappresenta un oggetto che utilizza un `ATemporalFormattLogger` per loggare
		l' inizio e la fine di un processo
	"""
	
	def __init__(
			self,
	        logger: ATemporalFormattLogger,
			mess_sep: str,
			end_mess: str="OK!"
	):
		"""
			Costruisce un nuovo ProcessLogger
			
			Parameters
			----------
				logger: ATemporalFormattLogger
					Un oggetto `ATemporalFormattLogger` rappresentante il logger da
					utilizzare per registrare l' inizio e la fine dei processi.
					
				mess_sep: str
					Una stringa contenente il separatore dei messaggi da utilizzare
					
				end_mess: str
					Opzionale. Default = `"OK!"`. Una stringa rappresentante il messaggio
					con cui concludere la buona riuscita di una serie di steps
		"""
		self._logger = logger
		self._mess_sep: str = mess_sep
		self._end_mess: str = end_mess
		
		self._log_frmt: str = None
		
		
	def process_start(self, message: str):
		"""
			Registra l' inizio di una serie di steps di un processo utilizzando
			il messaggio fornito
			
			Parameters
			----------
				message: str
					Una stringa contenente il messaggio da utilizzare per segnare
					l' inizio del processo voluto
					
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il parametro `message` ha valore `None`
						- Il parametro `message` è una stringa vuota
		"""
		if (message == "") or (message is None):
			raise ValueError()
		
		self._log_frmt = self._logger.unset_format()
		self._logger.set_messages_sep(" ")
		self._logger.log(message)
		
		
	def process_end(self):
		"""
			Registra la fine di una serie di steps di un processo
		"""
		self._logger.set_format(self._log_frmt)
		self._logger.set_messages_sep(self._mess_sep)
		self._logger.log(self._end_mess)
		
		
	def set_endmessage(self, end_message: str):
		"""
			Imposta un nuovo messaggio per indicare la fine del processo
			
			Parameters
			----------
				end_message: str
					Una stringa contenente il messaggio da utilizzare per segnare
					la fine dei prossimi processi
			
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il parametro `end_message` ha valore `None`
						- Il parametro `end_message` è una stringa vuota
		"""
		if (end_message == "") or (end_message is None):
			raise ValueError()
		
		self._end_mess = end_message
		
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================