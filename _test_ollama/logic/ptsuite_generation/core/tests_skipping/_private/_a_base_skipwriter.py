from abc import abstractmethod
from .. import ISkipWriter

# ============ Path Utilities ============ #
from os.path import splitext as path_split_ext
# ======================================== #
# ============== OS Utilities ============== #
from os.path import exists as os_fdexists
# ========================================== #

from ..exceptions import InvalidSkippedTestsFileError



class _ABaseSkipWriter(ISkipWriter):
	"""
		Rappresenta un `ISkipWriter` di base, ovvero che contiene la logica
		comune ad ogni `ISkipWriter`.
		
		Il tipo del file dei tests saltati è specificato dai discendenti di questa classe astratta.
		Il formato del file dei tests saltati è specificato dai discendenti di questa classe astratta.
	"""
	
	def __init__(
			self,
			skipdtests_path: str
	):
		"""
			Costruisce un nuovo _ABaseSkipWriter associandolo alla path
			che contiene, o conterrà, il file dei tests saltati
			
			Parameters
			----------
				skipdtests_path: str
					Una stringa rappresentante la path che contiene, o conterrà,
					il file dei tests saltati da utilizzare
					 
			Raises
			------
				ValueError
					Si verifica se:
						
						- Il parametro `skipdtests_path` ha valore `None`
						- Il parametro `skipdtests_path` è una stringa vuota
			
				InvalidSkippedTestsFileError
					Si verifica se il file è invalido per tipo o formato
		"""
		if (skipdtests_path is None) or (skipdtests_path == ""):
			raise ValueError()
		
		self._skipd_path: str = skipdtests_path
		
		
	def _p__file_extension(self) -> str:
		"""
			Restituisce l' estensione che è necessaria per il file dei
			tests saltati.
			
			L' implementazione di questo metodo è opzionale se per il tipo di file
			non è necessaria una particolare estensione
			
			Returns
			-------
				str
					Una stringa, in lowercase e senza punto, contenente l' estensione
					che il file dei tests saltati deve avere.
		"""
		return ""
		
		
	def _pf__get_skipdf_path(self) -> str:
		"""
			Restituisce la path che contiene il file dei tests saltati
			
			Returns
			-------
				str
					Una stringa rappresentante la path che contiene il file dei tests
					saltati da utilizzare
		"""
		return self._skipd_path
	
	
	def _P__objinit(self):
		"""
			Verifica/assicura gli invarianti dell' oggetto appena costruito
			
			Raises
			------
				InvalidSkippedTestsFileError
					Si verifica se la path non rappresenta un file di tests saltati di tipo,
					o formato, compatibili quelli specificati dai discendenti di questa
					classe astratta.
		"""
		extens: str = self._p__file_extension()
		if extens != "":
			if path_split_ext(self._skipd_path)[1].lower() != f".{extens}":
				raise InvalidSkippedTestsFileError()
			
		if os_fdexists(self._skipd_path):
			self._ap__assert_skipdtests_file(self._skipd_path)
		else:
			open(self._skipd_path, "w").close()
			self._ap__init_skipdtests_file(self._skipd_path)
		
		
	#	============================================================
	#						ABSTRACT METHODS
	#	============================================================
	
	
	@abstractmethod
	def _ap__assert_skipdtests_file(
			self,
			skipdtests_path: str
	):
		"""
			Controlla che il file dei tests saltati, alla path specificata, sia valido
			secondo il tipo e formato specificato dai discendenti di questa classe astratta.
			
			Se il file dei tests saltati è valido quest' operazione è equivalente ad una no-op.
			
			E' garantito all' interno di questo metodo:
				
				- Che il parametro `skipdtests_path` non abbia valore `None`
				- Che il parametro `skipdtests_path` non sia una stringa vuota
				- Che il file alla path `skipdtests_path` esiste
				- Che il parametro `skipdtests_path` punti a un file con l' estensione corretta
			
			Parameters
			----------
				skipdtests_path: str
					Una stringa rappresentante la path che contiene il file dei tests saltati
					da utilizzare
					
			Raises
			------
				InvalidSkippedTestsFileError
					Si verifica se il file è invalido per tipo o formato
		"""
		pass
	
	
	@abstractmethod
	def _ap__init_skipdtests_file(
			self,
			skipdtests_path: str
	):
		"""
			Inizializza il file dei tests saltati in base al formato del file specificato
			dai discendenti di questa classe astratta.
			
			Se il file dei tests saltati è valido quest' operazione è equivalente ad una no-op.
			
			E' garantito all' interno di questo metodo:
				
				- Che il parametro `skipdtests_path` non abbia valore `None`
				- Che il parametro `skipdtests_path` non sia una stringa vuota
				- Che il file alla path `skipdtests_path` è vuoto
			
			Parameters
			----------
				skipdtests_path: str
					Una stringa rappresentante la path che contiene il file dei tests saltati
					da utilizzare
		"""
		pass
	
	
	@abstractmethod
	def write_skipd_test(self, entity_name: str):
		pass