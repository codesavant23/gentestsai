from typing import Dict, Any
from abc import abstractmethod
from .. import IConfigParser

# ============ Path Utilities ============ #
from os.path import splitext as path_split_ext
# ======================================== #

from ....utils.path_validator import PathValidator

from ..exceptions import (
	InvalidConfigFilepathError,
	WrongConfigFileTypeError
)



class _ABaseConfigParser(IConfigParser):
	"""
		Rappresenta un `IConfigParser` di base, ovvero che contiene la logica di controllo
		comune ad ogni `IConfigParser`.
		
		Il tipo del file di configurazione letto è specificato dai discendenti di questa classe astratta.
		Il formato del file di configurazione letto è specificato dai discendenti di questa classe astratta
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo _ABaseConfigReader
		"""
		self._path_val: PathValidator = PathValidator()

	
	def read_config(
			self,
			cfgfile_path: str
	) -> Dict[str, Any]:
		if cfgfile_path is None:
			raise ValueError()
		if cfgfile_path == "":
			raise ValueError()
		
		try:
			self._path_val.assert_path(cfgfile_path)
		except Exception as err:
			raise InvalidConfigFilepathError(err.args[0])
		
		extens: str = self._p__file_extension()
		if extens != "":
			if path_split_ext(cfgfile_path)[1].lower() != f".{extens}":
				raise WrongConfigFileTypeError()
			
		return self._ap__read_spec(cfgfile_path)
	
	
	def _p__file_extension(self) -> str:
		"""
			Restituisce l' estensione necessaria per il file di configurazione.
			
			L' implementazione di questo metodo è opzionale se per il tipo di file
			non è necessaria una particolare estensione
			
			Returns
			-------
				str
					Una stringa, in lowercase e senza punto, contenente l' estensione
					di file accettata da questo `IConfigReader`
		"""
		return ""
	
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	
	
	@abstractmethod
	def _ap__read_spec(
			self,
			cfg_path: str
	) -> Dict[str, Any]:
		"""
			Verifica la validità del contenuto del file di configurazione associato rispetto
			al tipo specificato dai discendenti di questa classe astratta,
			e, se la validazione va a buon fine, ne restituisce il dizionario Python risultante.
			
			E' garantito all' interno di questo metodo:
				
				- Che il parametro `config_dict` non abbia valore `None`
				- Che il parametro `config_dict` non sia una stringa vuota
				- Che il file alla path `config_dict` esiste
				- Che il parametro `config_dict` punti a un file con l' estensione corretta
			
			Parameters
			----------
				cfg_path: str
					Una stringa rappresentante la path assoluta contenente il file di configurazione
					da associare e leggere
					
			Returns
			-------
				Dict[str, Any]
					Un dizionario variegato, indicizzato da stringhe, rappresentante il file di
					configurazione letto.
			
			Raises
			------
				WrongConfigFileTypeError
					Si verifica se il contenuto del file è invalido per il tipo specificato dai discendenti
					di questa classe astratta
					
				WrongConfigFileFormatError
					Si verifica se il file di configurazione non è rappresentabile come un dizionario Python
		"""
		pass
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================