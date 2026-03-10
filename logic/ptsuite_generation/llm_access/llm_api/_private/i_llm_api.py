from abc import ABC, abstractmethod



class ILlmApi(ABC):
	"""
		Rappresenta un API, o piattaforma di inferenza, di LLMs.
		Ogni ILlmApi è immutabile.
		
		Ogni ILlmApi è hashabile (tramite`.__hash__(...)`) e comparabile
		(tramite `.__eq__(...)`)
		
		L' API di LLMs rappresentata è specificata dai discendenti di questa interfaccia.
	"""
	
	
	@abstractmethod
	def api_name(self) -> str:
		"""
			Restituisce il nome che identifica l' API rappresentata
			
			Returns
			-------
				str
					Una stringa, lowercase, contenente il nome dell' API di LLMs rappresentata
					dai discendenti di questa interfaccia
		"""
		pass