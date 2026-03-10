from abc import ABC, abstractmethod



class IBuildCacheCleaner(ABC):
	"""
		Rappresenta un oggetto in grado di effettuare la pulizia della cache
		di building di un' immagine relativamente al "Container Manager"
		a cui è legato
		
		Il "Container Manager" per cui effettua la pulizia della cache è specificato
		dai discendenti di questa interfaccia.
	"""


	@abstractmethod
	def clean_buildcache(self):
		"""
			Effettua la pulizia della cache di building relativamente al "Container Manager"
			specificato dai discendenti di questa interfaccia
		"""
		pass