from typing import Dict, Any
from abc import abstractmethod
from .. import IConfigReader

# ============ Path Utilities ============ #
from os.path import splitext as path_split_ext
from pathlib import Path as SystemPath
# ======================================== #

from ..exceptions import (
	InvalidConfigFilepathError,
	WrongConfigFileTypeError
)



class ACheckableConfigReader(IConfigReader):
	"""
		Rappresenta un `IConfigReader` che fornisce un meccanismo di controllo per tipo e formato
		del file di configurazione da leggere che viene associato a questo lettore.
		
		La semantica del file di configurazione letto è specificata dai discendenti di questa interfaccia.
		Il tipo del file di configurazione letto è specificato dai discendenti di questa interfaccia.
		Il formato del file di configurazione letto è specificato dai discendenti di questa interfaccia.
		Il formato del dizionario risultante è specificato dai discendenti di questa interfaccia.
	"""
	
	def __init__(
			self,
			cfgfile_path: str
	):
		"""
			Costruisce un nuovo ACheckableConfigReader fornendogli la path del file di configurazione
			che verrà associato a questo lettore
			
			Parameters
			----------
				cfgfile_path: str
					Una stringa rappresentante la path assoluta contenente il file di configurazione
					da associare e leggere
			
			Raises
			------
				ValueError
					Si verifica se:
					
						- La path del file di configurazione fornita ha valore `None`
						- La path del file di configurazione fornita è una stringa vuota
						
				WrongConfigFileTypeError
					Si verifica se:
						
						- Il file di configurazione dato non è un file del tipo specificato dai
						  discendenti di questa classe astratta
						- Il file è invalido per il tipo specificato dai discendenti di questa
						  classe astratta
					
				InvalidConfigFilepathError
					Si verifica se:
					
						- La path del file di configurazione fornita risulta invalida sintatticamente
						- Non è possibile aprire il file di configurazione
		"""
		self._assert_configfile_correctness(cfgfile_path)
		self._cfgfile_path = cfgfile_path
	
	
	def read_config(self) -> Dict[str, Any]:
		config_read: Dict[str, Any] = self._ap__read_spec_config()
		
		self._ap__assert_fields(config_read)
		
		return self._ap__format_result(config_read)
	
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	
	
	@abstractmethod
	def _ap__read_spec_config(self) -> Dict[str, Any]:
		"""
			Legge il file di configurazione associato, eseguendo le necessarie operazioni
			in base alla semantica, tipo e formato specifici restituendone il dizionario
			Python che ne risulta.
			
			Si fornisce il metodo `self._pf__get_cfgfile_path(...)` per ottenere la path del
			file di configurazione associato da leggere.
			
			Returns
			-------
				Dict[str, Any]
					Un dizionario variegato, indicizzato su stringhe, rappresentante il file di
					configurazione associato letto
					
			Raises
			------
				WrongConfigFileFormatError
					Si verifica se il file di configurazione non è rappresentabile come un dizionario Python
		"""
		pass
	
	
	@abstractmethod
	def _ap__assert_fields(
			self,
			config_read: Dict[str, Any]
	):
		"""
			Controlla la validità dei campi che dovrebbero essere contenuti nel file di configurazione che è stato
			letto da questo ACheckableConfigReader.
			
			Se la validazione va a buon fine quest' operazione deve essere equivalente ad una no-op.
			
			Raises
			------
				FieldDoesntExistsError
					Si verifica se il file di configurazione letto ha uno più campi obbligatori mancanti
			
				WrongConfigFileFormatError
					Si verifica se:
						
						- Il file di configurazione non è rappresentabile come un dizionario Python
						- Il file di configurazione contiene campi non previsti dal formato specificato
						  dai discendenti di questa classe astratta

				InvalidConfigurationValueError
					Si verifica se:
					
						- La semantica di uno o più campi obbligatori è errata
						- La semantica di uno o più campi opzionali è errata
						- La semantica di uno o più campi è corretta ma sussiste un errore specifico dichiarato
						  dai discendenti di questa classe astratta
		"""
		pass
	
	
	@abstractmethod
	def _ap__format_result(
			self,
			config_read: Dict[str, Any]
	) -> Dict[str, Any]:
		"""
			Formatta il dizionario associato al file di configurazione letto nel formato
			specificato dai discendenti di questa classe astratta
			
			Parameters
			----------
				config_read: Dict[str, Any]
					Un dizionario variegato, indicizzato su stringhe, contenente i parametri di configurazione
					specificati nel contratto dei discendenti di questa classe astratta, restituiti all' utilizzatore
					di questo ACheckableConfigReader
		"""
		pass
	
	
	@abstractmethod
	def _ap__accepted_extension(self) -> str:
		"""
			Restituisce l' estensione di file accettata da questo ACheckableConfigReader in base
			al tipo specificato dai discendenti di questa classe astratta
			
			Returns
			-------
				str
					Una stringa contenente l' estensione di file accettata da questo
					ACheckableConfigReader senza il carattere "." che la precede
		"""
		pass
	
	
	@abstractmethod
	def _ap__assert_type_correctness(
			self,
			cfgfile_path: str
	):
		"""
			Verifica la validità del file di configurazione associato rispetto al
			tipo specificato dai discendenti di questa classe astratta.
			
			Se il file di configurazione è valido quest' operazione è equivalente ad una no-op
			
			Parameters
			----------
				cfgfile_path: str
					Una stringa rappresentante la path assoluta contenente il file di configurazione
					da associare e leggere
			
			Raises
			------
				WrongConfigFileTypeError
					Si verifica se il file è invalido per il tipo specificato dai discendenti
					di questa classe astratta
		"""
		pass
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================
	
	
	def _pf__get_cfgfile_path(self) -> str:
		"""
			Restituisce la path del file di configurazione che è stato associato
			a questo ACheckableConfigReader
			
			Returns
			-------
				str
					Una stringa rappresentante la path che contiene il file di configurazione
					che è stato associato a quest' oggetto
		"""
		return self._cfgfile_path


	def _assert_configfile_correctness(
			self,
			cfgfile_path: str
	):
		"""
			Verifica se il file di configurazione da associare e leggere in questo ACheckableConfigReader:
			
				- Ha una path valida
				- E' leggibile
				- Rispetta l' estensione ed è valido per il tipo specificato dai discendenti
				  di questa classe astratta
		
			Raises
			------
				ValueError
					Si verifica se:
					
						- La path del file di configurazione fornita ha valore `None`
						- La path del file di configurazione fornita è una stringa vuota
						
				WrongConfigFileTypeError
					Si verifica se:
						
						- Il file di configurazione dato non è un file del tipo specificato dai
						  discendenti di questa classe astratta
						- Il file è invalido per il tipo specificato dai discendenti di questa
						  classe astratta
						
				InvalidConfigFilepathError
					Si verifica se:
					
						- La path del file di configurazione fornita risulta invalida sintatticamente
						- Non è possibile aprire il file di configurazione
		"""
		if cfgfile_path is None:
			raise ValueError()
		if cfgfile_path == "":
			raise ValueError()
		
		extens: str = path_split_ext(cfgfile_path)[1].lower()
		acc_extens: str = "."+self._ap__accepted_extension().lower()
		if extens != acc_extens:
			raise WrongConfigFileTypeError()

		try:
			prompts_path = SystemPath(cfgfile_path)
			prompts_path.stat()
		except (FileNotFoundError,
		        PermissionError,
		        OSError):
			raise InvalidConfigFilepathError()
		
		self._ap__assert_type_correctness(cfgfile_path)