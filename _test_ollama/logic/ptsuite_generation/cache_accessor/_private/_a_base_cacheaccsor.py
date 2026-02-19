from typing import Set
from abc import abstractmethod
from .. import IPtsuiteCacheAccessor

# ============ Path Utilities ============ #
from os.path import splitext as path_split_ext
# ======================================== #
# ============== OS Utilities ============== #
from os.path import (
	exists as os_fdexists,
	isfile as os_isfile,
)
# ========================================== #

from ..exceptions import (
	CacheFileTypeError,
	ProjectSpaceNotExistsError,
	EntryAlreadyExistsError,
	EntryNotExistsError
)



class _ABaseCacheAccessor(IPtsuiteCacheAccessor):
	"""
		Rappresenta un `IPtsuiteCacheAccessor` di base, ovvero che contiene la logica comune ad ogni `IPtsuiteCacheAccessor`
		
		La tecnologia implementativa della cache è specificata dai discendenti di questa classe astratta.
		Lo scopo di utilizzo della cache è specificata dai discendenti di questa classe astratta.
	"""
	
	def __init__(self, cache_path: str):
		"""
			Costruisce un nuovo _ABaseCacheAccessor associandolo alla
			cache che verrà utilizzata
			
			Parameters
			----------
				cache_path: str
					Una stringa rappresentante la path contenente il file di caching che
					verrà utilizzato
					
			Raises
			------
				ValueError
					Si verifica se:
						
						- Il parametro `cache_path` ha valore `None`
						- Il parametro `cache_path` è una stringa vuota
						
				OSError
					Si verifica se non esiste un file alla path `cache_path` data
		"""
		if (cache_path is None) or (cache_path == ""):
			raise ValueError()
		if not os_fdexists(cache_path):
			raise OSError()
		if not os_isfile(cache_path):
			raise OSError()
		
		self._cache_path: str = cache_path
		self._proj_spaces: Set[str] = set()
	
	
	def create_projspace(self, proj_name: str):
		if (proj_name is None) or (proj_name == ""):
			raise ValueError()
		
		self._ap__create_projspace_spec(proj_name)
		
		self._proj_spaces.add(proj_name)
	
		
	def register_ptsuite(
			self,
			proj_name: str,
			prompt: str, model: str, try_num: int,
			ptsuite_code: str
	):
		if ((proj_name is None) or (proj_name == "") or
			(prompt is None) or (prompt == "") or
			(model is None) or (model == "") or
			(ptsuite_code is None) or (ptsuite_code == "")
		):
			raise ValueError()
		
		if proj_name not in self._proj_spaces:
			raise ProjectSpaceNotExistsError()
		
		if self.does_ptsuite_exists(proj_name, prompt, model, try_num):
			raise EntryAlreadyExistsError()
		
		self._ap__register_ptsuite_spec(
			proj_name,
			prompt, model, try_num,
			ptsuite_code
		)
		
	
	def get_ptsuite(
			self,
			proj_name: str,
			prompt: str, model: str, try_num: int
	) -> str:
		if ((proj_name is None) or (proj_name == "") or
			(prompt is None) or (prompt == "") or
			(model is None) or (model == "")
		):
			raise ValueError()
		
		if proj_name not in self._proj_spaces:
			raise ProjectSpaceNotExistsError()
		
		if not self.does_ptsuite_exists(proj_name, prompt, model, try_num):
			raise EntryNotExistsError()
		
		return self._ap__get_ptsuite_spec(
			proj_name, prompt, model, try_num
		)
	
	
	def _pf__get_cache_path(self) -> str:
		"""
			Restituisce la path che contiene il file di caching
			
			Returns
			-------
				str
					Una stringa rappresentante la path che contiene il file di caching
					da utilizzare
		"""
		return self._cache_path
	
	
	def _p__file_extension(self) -> str:
		"""
			Restituisce l' estensione che è necessaria per il file di caching
			
			L' implementazione di questo metodo è opzionale se per il tipo di file
			non è necessaria una particolare estensione
			
			Returns
			-------
				str
					Una stringa, in lowercase e senza punto, contenente l' estensione
					che il file di caching deve avere.
		"""
		return ""
	
	
	def _P__objinit(self):
		"""
			Verifica/assicura gli invarianti dell' oggetto appena costruito
			
			Raises
			------
				CacheFileTypeError
					Si verifica se la path non rappresenta un file di caching compatibile
					con la tecnologia implementativa specificata dai discendenti di questa
					classe astratta.
		"""
		extens: str = self._p__file_extension()
		if extens != "":
			if path_split_ext(self._cache_path)[1].lower() != f".{extens}":
				raise CacheFileTypeError()
			
		self._ap__assert_cache_type(self._cache_path)
	
	
	#	============================================================
	#						ABSTRACT METHODS
	#	============================================================
	
	
	@abstractmethod
	def _ap__assert_cache_type(self, cache_path: str):
		"""
			Verifica se la cache fornita come argomento è compatibile con la tecnologia implementativa
			della cache rappresentata dai discendenti di questa classe astratta.
			
			Se la verifica ha successo quest' operazione è equivalente ad una no-op.
			
			E' garantito all' interno di questo metodo:
			
				- Che il parametro `cache_path` non abbia valore `None`
				- Che il parametro `cache_path` non sia una stringa vuota
				- Che il file alla path `cache_path` esista
				- Che il parametro `cache_path` punti a un file con l' estensione corretta
			
			Parameters
			----------
				cache_path: str
					Una stringa rappresentante la path contenente il file di caching
					da verificare
		"""
		pass
	
	
	@abstractmethod
	def _ap__create_projspace_spec(self, proj_name: str):
		"""
			Riserva lo spazio di memorizzazione necessario per le test-suites parziali
			del progetto focale di cui viene fornito il nome.
			
			Se lo spazio di memorizzazione esiste già quest' operazione è equivalente ad una no-op.
			
			E' garantito all' interno di questo metodo:
			
				- Che il parametro `proj_name` non abbia valore `None`
				- Che il parametro `proj_name` non sia una stringa vuota
			
			Parameters
			----------
				proj_name: str
					Una stringa contenente il nome del nuovo progetto di cui riservare
					lo spazio di memorizzazione nella cache rappresentata
					
			Raises
			------
				ProjectSpaceReservationError
					Si verifica se avviene un errore nel riservare lo spazio di memorizzazione
		"""
		pass
	
	
	@abstractmethod
	def _ap__register_ptsuite_spec(self,
	        proj_name: str,
			prompt: str, model: str, try_num: int,
			ptsuite_code: str
	):
		"""
			Registra un nuovo tentativo di produzione di una test-suite parziale
			nella cache rappresentata
			
			E' garantito all' interno di questo metodo:
				
				- Che `try_num >= 0`
				- Che nessun parametro stringa sia `None` nè stringa vuota
				- Che lo spazio di memorizzazione del progetto `proj_name` esista
				- Che non esiste già un tentativo corrispondente alla quadrupla
				  (`proj_name`, `prompt`, `model`, `try_num`)
			
		
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
		"""
		pass
	
	
	@abstractmethod
	def _ap__get_ptsuite_spec(
			self,
	        proj_name: str,
			prompt: str, model: str, try_num: int
	) -> str:
		"""
			Restituisce il tentativo di produzione di una test-suite parziale, nella cache rappresentata,
			associata alle seguenti caratteristiche.
			
			E' garantito all' interno di questo metodo:
			
				- Che `try_num >= 0`
				- Che nessun parametro stringa sia `None` nè stringa vuota
				- Che lo spazio di memorizzazione del progetto `proj_name` esista
				- Che esiste un tentativo corrispondente alla quadrupla
				  (`proj_name`, `prompt`, `model`, `try_num`)
				  
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
		"""
		pass
	
	
	@abstractmethod
	def does_ptsuite_exists(self, proj_name: str, prompt: str, model: str, try_num: int) -> bool:
		pass
		
		
	#	============================================================
	#						PRIVATE METHODS
	#	============================================================


	def __enter__(self):
		return self


	def __exit__(self, exc_type: type, exc: Exception, traceback):
		self.close()