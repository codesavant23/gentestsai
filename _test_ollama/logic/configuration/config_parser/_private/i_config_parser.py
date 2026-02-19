from typing import Dict, Any
from abc import ABC, abstractmethod



class IConfigParser(ABC):
	"""
		Rappresenta un parser di files di configurazione, di GenTestsAI, scritti in uno specifico tipo e formato.
		La categoria di files di configurazione che possono essere letti da ogni IConfigParser sono files
		di configurazione rappresentabili come un dizionario Python (con valori variegati) indicizzato da stringhe.
		
		Il tipo del file di configurazione letto è specificato dai discendenti di questa interfaccia.
	"""


	@abstractmethod
	def read_config(self, cfgfile_path: str) -> Dict[str, Any]:
		"""
			Effettua il parsing del file di configurazione alla path specificata, verificando:
				
				- Se, eventualmente, l' estensione è quella richiesta dal tipo
				- Se il contenuto è valido per il tipo specificato dai discendenti di questa interfaccia
				- Se il file di configurazione è rappresentabile come un dizionario Python
				
			Successivamente legge il file di configurazione restituendolo come dizionario Python
			di valori variegati
			
			Parameters
			----------
				cfgfile_path: str
					Una stringa contenente la path del file di configurazione di cui effettuare
					il parsing
			
			Returns
			-------
				Dict[str, Any]
					Un dizionario variegato, indicizzato da stringhe, rappresentante il file di
					configurazione letto.
					
			Raises
			------
				ValueError
					Si verifica se:
					
						- La path del file di configurazione fornita ha valore `None`
						- La path del file di configurazione fornita è una stringa vuota
						
				InvalidConfigFilepathError
					Si verifica se:
					
						- La path del file di configurazione fornita risulta invalida sintatticamente
						- Non esiste un file alla path fornita
						- Non è possibile aprire il file di configurazione
			
				WrongConfigFileTypeError
					Si verifica se:
						
						- Il file di configurazione associato non è un file del tipo specificato dai
						  discendenti di questa interfaccia (estensione)
						- Il contenuto del file è invalido per il tipo specificato dai discendenti
						  di questa interfaccia
						  
				WrongConfigFileFormatError
					Si verifica se il file di configurazione non è rappresentabile come un dizionario Python
		"""
		pass