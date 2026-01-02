from abc import abstractmethod
from .. import ISkipWriter



class AInitializableSkipWriter(ISkipWriter):
	"""
		Rappresenta uno `ISkipWriter` il cui file dei tests saltati a cui è stato associato
		ha bisogno di essere inizializzato.
		
		Il tipo del file dei tests saltati è specificato dai discendenti di questa classe astratta.
		Il formato del file dei tests saltati è specificato dai discendenti di questa classe astratta.
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo AInitializableSkipWriter
		"""
		pass
	
	
	#	============================================================
	#						ABSTRACT METHODS
	#	============================================================
	
	
	@abstractmethod
	def _ap__init_skipdtests_file(
			self,
			skipdtests_path: str
	):
		"""
			Inizializza il file dei tests saltati in base al formato del file specificato
			dai discendenti di questa classe astratta
			
			Parameters
			----------
				skipdtests_path: str
					Una stringa rappresentante la path che contiene il file dei tests saltati
					da utilizzare
		"""
		pass