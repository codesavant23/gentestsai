from abc import ABC, abstractmethod



class ILogger(ABC):
	"""
		Rappresenta un oggetto in grado di registrare, tramite uno stream di output testuale,
		messaggi per tracciare gli steps svolti durante l' esecuzione di un processo.
		
		Lo scopo dei messaggi di logging è specificato dai discendenti di questa interfaccia.
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
