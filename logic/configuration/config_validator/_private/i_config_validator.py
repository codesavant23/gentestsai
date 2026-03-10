from abc import ABC, abstractmethod



class IConfigValidator(ABC):
	"""
		Rappresenta un validatore di files di configurazione, di GenTestsAI, riguardanti uno specifico scopo,
		rappresentati tramite un dizionario Python (con valori variegati) indicizzato da stringhe.
		
		Lo scopo del file di configurazione validato è specificato dai discendenti di questa interfaccia.
	"""
	
	
	@abstractmethod
	def validate_sem(self):
		"""
			Effettua la validazione semantica del dizionario Python associato rappresentante
			il file di configurazione
		
			Raises
			------
				FieldDoesntExistsError
					Si verifica se il file di configurazione rappresentato ha uno più campi
					obbligatori mancanti
			
				ConfigExtraFieldsError
					Si verifica se il file di configurazione contiene campi non previsti
					dallo scopo specificato dai discendenti di questa interfaccia

				InvalidConfigValueError
					Si verifica se:
					
						- La semantica di uno o più campi obbligatori è errata
						- La semantica di uno o più campi opzionali è errata
						- La semantica di uno o più campi è corretta ma sussiste un errore specifico
						  dichiarato dai discendenti di questa interfaccia
		"""
		pass