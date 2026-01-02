from typing import Dict, Any
from abc import ABC, abstractmethod



class IConfigReader(ABC):
	"""
		Rappresenta un lettore di files di configurazione, di GenTestsAI, scritti in uno specifico tipo e formato.
		La categoria di files di configurazione che possono essere letti da ogni IConfigurationReader sono files
		di configurazione rappresentabili come un dizionario Python (con valori variegati) indicizzato da stringhe.
		
		La semantica del file di configurazione letto è specificata dai discendenti di questa interfaccia.
		Il tipo del file di configurazione letto è specificato dai discendenti di questa interfaccia.
		Il formato del file di configurazione letto è specificato dai discendenti di questa interfaccia.
		Il formato del dizionario risultante è specificato dai discendenti di questa interfaccia.
	"""


	@abstractmethod
	def read_config(
			self,
	) -> Dict[str, Any]:
		"""
			Legge il file di configurazione associato a questo IConfigReader.
			
			La semantica del file di configurazione letto è specificata dai discendenti di questa interfaccia.
			Il tipo del file di configurazione letto è specificato dai discendenti di questa interfaccia.
			Il formato del file di configurazione letto è specificato dai discendenti di questa interfaccia.
					
			Returns
			-------
				Dict[str, Any]
					Un dizionario variegato, indicizzato da stringhe, rappresentante il file di
					configurazione letto.
					Le chiavi e gli elementi contenuti nel dizionario sono specificati dai discendenti
					di quest' interfaccia
					
			Raises
			------
				FieldDoesntExistsError
					Si verifica se il file di configurazione letto ha uno più campi obbligatori mancanti
			
				WrongConfigFileFormatError
					Si verifica se:
						
						- Il file di configurazione non è rappresentabile come un dizionario Python
						- Il file di configurazione contiene campi non previsti dal formato specificato
						  dai discendenti di questa interfaccia

				InvalidConfigValueError
					Si verifica se:
					
						- La semantica di uno o più campi obbligatori è errata
						- La semantica di uno o più campi opzionali è errata
						- La semantica di uno o più campi è corretta ma sussiste un errore specifico dichiarato
						  dai discendenti di questa interfaccia
		"""
		pass