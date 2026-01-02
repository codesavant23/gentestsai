from abc import abstractmethod
from .. import AInitializableSkipWriter



class AMutableInitializableSkipWriter(AInitializableSkipWriter):
	"""
		Rappresenta un `AInitializableSkipWriter` che può variare il file, dei tests saltati,
		a cui è stato associato.
		
		Il tipo del file dei tests saltati è specificato dai discendenti di questa classe astratta.
		Il formato del file dei tests saltati è specificato dai discendenti di questa classe astratta.
	"""
	
	def __init__(
			self,
			skipdtests_path: str
	):
		"""
			Costruisce un nuovo AMutableInitializableSkipWriter
			
			Parameters
			----------
				skipdtests_path: str
					Una stringa rappresentante la path che conterrà il file dei tests saltati
					da utilizzare
					 
			Raises
			------
				InvalidSkippedTestsFileError
					Si verifica se il file è invalido per tipo o formato
					
		"""
		super().__init__()
		
		self._skipd_path: str = None
		self.set_skiptests_file(skipdtests_path)
		
		
	def set_skiptests_file(
			self,
			skipdtests_path: str
	):
		"""
			Imposta un nuovo file dei tests saltati da associare a questo
			AMutableInitializableSkipWriter dissociando il precedente
			
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
		self._ap__assert_skipdtests_file(skipdtests_path)
		
		self._ap__init_skipdtests_file(skipdtests_path)
		self._skipd_path = skipdtests_path
		
		
	def get_skiptests_file(self) -> str:
		"""
			Restituisce la path del file dei tests saltati impostato per ultimo
			
			Returns
			-------
				str
					Una stringa rappresentante la path che contiene il file dei tests
					saltati impostato per ultimo
		"""
		return self._skipd_path
		
		
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