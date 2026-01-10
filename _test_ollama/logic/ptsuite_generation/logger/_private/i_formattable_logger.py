from abc import ABC, abstractmethod



class IFormattableLogger(ABC):
	"""
		Rappresenta un oggetto in grado di registrare, tramite uno stream di output testuale,
		messaggi per tracciare gli steps svolti durante l' esecuzione di un processo, opzionalmente
		in modo formattato.
		
		Ogni stringa di formato è caratterizzata dalla presenza, o assenza, di determinati placeholders
		per includere informazioni variabili nei messaggi di log.
		La stringa di formato di base definisce come:
		
			- "{message}": Il placeholder che contiene il messaggio fornito al metodo `.log(...)`
		
		Il tipo di stream di output è specificato dai discendenti di questa classe astratta.
		Altri placeholders del formato sono specificati dai discendenti di questa classe astratta.
	"""
	
	
	@abstractmethod
	def log(self, message: str):
		"""
			Registra un nuovo messaggio sullo stream di output fornito
			
			Parameters
			----------
				message: str
					Una stringa contenente il messaggio da registrare sullo stream di output
		"""
		pass


	@abstractmethod
	def set_format(self, format_str: str):
		"""
			Imposta una nuova stringa di formato da utilizzare per formattare i messaggi
			che verranno registrati tramite questo IFormattableLogger
			
			Parameters
			----------
				format_str: str
					Una stringa rappresentante la stringa di formato che verrà utilizzata
					per la formattazione dei prossimi messaggi che verranno registrati
				
			Raises
			------
				InvalidFormatError
					Si verifica se è stato fornito un formato con placeholders differenti da quelli
					accettabili dai discendenti di questa interfaccia
		"""
		pass
	
	
	@abstractmethod
	def unset_format(self):
		"""
			Elimina la stringa di formato precedentemente impostata così da riportare il messaggio
			registrato senza nessuna formattazione
			
			Raises
			------
				FormatNotSetError
					Si verifica se non c'è una stringa di formato impostata alla chiamata di
					questa operazione
		"""
		pass