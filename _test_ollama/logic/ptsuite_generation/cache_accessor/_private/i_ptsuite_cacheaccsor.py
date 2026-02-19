from abc import ABC, abstractmethod



class IPtsuiteCacheAccessor(ABC):
	"""
		Rappresenta un oggetto che permette di accedere ad una cache di test-suites parziali che sono
		risultanti da un processo in cui si utilizzano Large Language Models.
		Ogni entry della cache è un tentativo di produrre, tramite LLM, una test-suite parziale funzionante.
		
		Ogni `IPtsuiteCacheAccessor` supporta il "Context Manager" di Python.
		
		La tecnologia implementativa della cache è specificata dai discendenti di questa interfaccia.
	"""
	

	@abstractmethod
	def close(self):
		"""
			Effettua il rilascio delle risorse utilizzate da questo cache accessor.
			La chiamata a quest' operazione è obbligatoria alla fine dell' utilizzo di questo
			`IPtsuiteCacheAccessor`.
			Se si utilizza quest' oggetto con "Context Manager" allora la chiamata a questa
			operazione è già assicurata
			
			Se non c'è da rilasciare nulla quest' operazione è equivalente ad una no-op.
		"""
		pass


	@abstractmethod
	def create_projspace(self, proj_name: str):
		"""
			Riserva lo spazio di memorizzazione necessario per le test-suites parziali
			del progetto focale di cui viene fornito il nome.
			
			Se lo spazio di memorizzazione esiste già quest' operazione è equivalente ad una no-op
			
			Parameters
			----------
				proj_name: str
					Una stringa contenente il nome del nuovo progetto di cui riservare
					lo spazio di memorizzazione nella cache rappresentata
					
			Raises
			------
				ValueError
					Si verifica se:
						
						- Il parametro `proj_name` ha valore `None`
						- Il parametro `proj_name` è una stringa vuota
			
				ProjectSpaceReservationError
					Si verifica se avviene un errore nel riservare lo spazio di memorizzazione
		"""
		pass
	
	
	@abstractmethod
	def register_ptsuite(
			self,
	        proj_name: str,
			prompt: str, model: str, try_num: int,
			ptsuite_code: str
	):
		"""
			Registra un nuovo tentativo di produzione di una test-suite parziale
			nella cache rappresentata
			
			Parameters
			----------
				proj_name: str
					Una stringa contenente il nome del progetto di cui registrare il tentativo
					di produzione della test-suite parziale
				
				prompt: str
					Una stringa contenente il prompt da cui risulta il tentativo di produrre
					la test-suite parziale da registrare nella cache
					
				model: str
					Una stringa rappresentante il nome del LLM da cui è stato prodotta il tentativo
					da registrare nella cache
					
				try_num: int
					Un intero indicante il numero del tentativo di generazione a cui corrisponde
					questa "versione" della test-suite parziale che si vuole registrare nella cache
					
				ptsuite_code: str
					Una stringa contenente il codice della test-suite parziale, prodotto dal tentativo del LLM,
					da registrare nella cache
					
			Raises
			------
				ValueError
					Si verifica se:
					
						- Almeno uno tra `proj_name`, `prompt`, `model` e `ptsuite_code` ha valore `None`
						- Almeno uno tra `proj_name`, `prompt`, `model` e `ptsuite_code` sono una stringa vuota
						- Il parametro `try_num` è minore di 0
			
				ProjectSpaceNotExistsError
					Si verifica se lo spazio di memorizzazione di `proj_name` non esiste
					
				EntryAlreadyExistsError
					Si verifica se esiste già un tentativo di produzione associato alla quaterna
					(`proj_name`, `prompt`, `model`, `try_num`) data
		"""
		pass
	
	
	@abstractmethod
	def does_ptsuite_exists(
			self,
	        proj_name: str,
			prompt: str, model: str, try_num: int
	) -> bool:
		"""
			Verifica se esiste un tentativo di produzione di una test-suite parziale
			nella cache rappresentata associata alle seguenti caratteristiche
			
			Parameters
			----------
				proj_name: str
					Una stringa contenente il nome del progetto di cui si cerca il tentativo
					di produzione della test-suite parziale
				
				prompt: str
					Una stringa contenente il prompt da cui risulterebbe il tentativo di produrre
					la test-suite parziale presente nella cache
					
				model: str
					Una stringa rappresentante il nome del LLM da cui sarebbe stato prodotto
					il tentativo presente nella cache
					
				try_num: int
					Un intero indicante il numero del tentativo di generazione a cui corrisponderebbe
					la "versione" della test-suite parziale cercata
					
			Returns
			-------
				bool
					Un booleano indicante se il tentativo cercato esiste nella cache rappresentata
		"""
		pass
	
	
	@abstractmethod
	def get_ptsuite(
			self,
	        proj_name: str,
			prompt: str, model: str, try_num: int
	) -> str:
		"""
			Restituisce il tentativo di produzione di una test-suite parziale, nella cache rappresentata,
			associata alle seguenti caratteristiche
			
			Parameters
			----------
				proj_name: str
					Una stringa contenente il nome del progetto di cui si cerca il tentativo
					di produzione della test-suite parziale
				
				prompt: str
					Una stringa contenente il prompt da cui risulta il tentativo di produrre
					la test-suite parziale presente nella cache
					
				model: str
					Una stringa rappresentante il nome del LLM da cui è stato prodotto
					il tentativo presente nella cache
					
				try_num: int
					Un intero indicante il numero del tentativo di generazione a cui corrisponde
					la "versione" della test-suite parziale cercata
		
			Returns
			-------
				str
					Una stringa contenente il codice della test-suite parziale, del tentativo cercato,
					nella cache rappresentata
					
			Raises
			------
				ValueError
					Si verifica se:
					
						- Almeno uno tra `proj_name`, `prompt`, `model` e `ptsuite_code` ha valore `None`
						- Almeno uno tra `proj_name`, `prompt`, `model` e `ptsuite_code` sono una stringa vuota
						- Il parametro `try_num` è minore di 0
			
				ProjectSpaceNotExistsError
					Si verifica se lo spazio di memorizzazione di `proj_name` non esiste
					
				EntryNotExistsError
					Si verifica se non esiste un tentativo di test-suite parziale associato
					alla quaterna (`proj_name`, `prompt`, `model`, `try_num`) data
		"""
		pass