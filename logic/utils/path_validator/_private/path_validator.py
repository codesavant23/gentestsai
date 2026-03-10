# ============ Path Utilities ============ #
from pathlib import Path as SystemPath
# ======================================== #

from .. import EPathValidationErrorType



class PathValidator:
	"""
		Rappresenta un validatore di paths di sistema
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo PathValidator
		"""
		self._synt_error: str = 'La path fornita è invalida sintatticamente'
		self._notex_error: str = 'La path fornita non esiste'
		self._perm_error: str = 'Non si può accedere alla path specificata. Mancano i permessi necessari'
		self._notre_error: str = 'La path fornita risulta inaccessibile'
		
	
	def set_error_msg(
			self,
			error: EPathValidationErrorType,
			error_msg: str
	):
		"""
			Imposta un messaggio diverso per il tipo di errore, legato alla validazione,
			che è stato specificato
			
			Parameters
			----------
				error: EPathValidationErrorType
					Un valore `EPathValidationErrorType` rappresentante il tipo di errore di
					validazione di cui modificare il messaggio specificato
					
				error_msg: str
					Una stringa contenente il nuovo messaggio di errore da impostare
		"""
		match error:
			case EPathValidationErrorType.SYNTACTIC:
				self._synt_error = error_msg
			case EPathValidationErrorType.NOTEXISTS:
				self._notex_error = error_msg
			case EPathValidationErrorType.PERMISSION:
				self._perm_error = error_msg
			case EPathValidationErrorType.INACCESSIBLE:
				self._notre_error = error_msg
	
		
	def assert_path(self, path: str):
		"""
			Verifica che la path fornita sia:
				
				- Corretta sintatticamente ed esista nel sistema operativo.
				- Sia raggiungibile
				- Sia accessibile (a livello di permessi)
			
			Parameters
			----------
				path: str
					Una stringa contenente la path di cui verificare la validità
			
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il parametro `path` ha valore `None`
						- Il parametro `path` è una stringa vuota
						
				NotADirectoryError
					Si verifica se la path è sintatticamente invalida
					
				FileNotFoundError
					Si verifica se la path non esiste
					
				PermissionError
					Si verifica se la path è inaccessibile a causa della mancanza di permessi
					
				OSError
					Si verifica se la path è inaccessibile per altra causa
		"""
		if (path is None) or (path == ""):
			raise ValueError()
		
		path: SystemPath
		try:
			path = SystemPath(path)
			path.stat()
		except NotADirectoryError:
			raise NotADirectoryError(self._synt_error)
		except FileNotFoundError:
			raise FileNotFoundError(self._notex_error)
		except PermissionError:
			raise PermissionError(self._perm_error)
		except OSError:
			raise OSError(self._notre_error)
		
		
		##	============================================================
		##						PRIVATE METHODS
		##	============================================================
