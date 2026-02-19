from .. import IPtsuiteCacheAccessor
from .e_cacheaccsor_type import ECacheAccessorType

from .._private._a_base_cacheaccsor import _ABaseCacheAccessor
from .._private.sqlite3_cacheaccsor import Sqlite3CacheAccessor



class PtsuiteCacheAccessorFactory:
	"""
		Rappresenta una factory per ogni `IPtsuiteCacheAccessor`
	"""
		
	
	@classmethod
	def create(
			cls,
			tech: ECacheAccessorType,
	        cache_path: str
	) -> IPtsuiteCacheAccessor:
		"""
			Istanzia un nuovo cache accessor della tecnologia implementativa specificata
			
			Parameters
			----------
				tech: ECacheAccessorType
					Un valore `ECacheAccessorType` rappresentante la tecnologia richiesta
					per l' oggetto `IPtsuiteCacheAccessor`
					
				cache_path: str
					Una stringa rappresentante la path che contiene il file di caching
					da utilizzare
					
			Returns
			-------
				IPtsuiteCacheAccessor
					Un oggetto `IPtsuiteCacheAccessor` che permette l' accesso a una cache
					della tecnologia implementativa specificata
					
			Raises
			------
				ValueError
					Si verifica se:
						
						- Il parametro `cache_path` ha valore `None`
						- Il parametro `cache_path` è una stringa vuota
						
				OSError
					Si verifica se non esiste un file alla path `cache_path` data
						
				CacheFileTypeError
					Si verifica se la path non rappresenta un file di caching compatibile
					con la tecnologia implementativa richiesta
		"""
		obj: _ABaseCacheAccessor
		match tech:
			case ECacheAccessorType.SQLITE3:
				obj = Sqlite3CacheAccessor(cache_path)
			
		obj._P__objinit()
		return obj
		
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================