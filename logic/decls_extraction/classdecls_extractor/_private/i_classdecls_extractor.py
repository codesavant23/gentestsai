from typing import List
from abc import ABC, abstractmethod



class IClassDeclsExtractor(ABC):
	"""
		Rappresenta un oggetto in grado di estrarre, e separare, il codice di una classe Python
		associata scomponendola nelle dichiarazioni dei metodi presenti al suo interno.
		
		La tecnologia implementativa utilizzata è specificata dai discendenti di questa interfaccia.
	"""
	
	
	@abstractmethod
	def class_name(self) -> str:
		"""
			Restituisce il nome della classe associata a questo IClassDeclsExtractor
			
			Returns
			-------
				str
					Una stringa contenente il nome della classe assoiata a quest' oggetto
		"""
		pass
	
	
	@abstractmethod
	def method_names(self) -> List[str]:
		"""
			Estrae i nomi dei metodi che sono definiti all' interno della classe associata
			
			Returns
			-------
				List[str]
					Una lista di stringhe contenente i nomi dei metodi definiti all' interno
					della classe associata
		"""
		pass
	
	
	@abstractmethod
	def methods(self) -> List[str]:
		"""
			Estrae le definizioni dei metodi che si trovano all' interno della classe associata
			
			Returns
			-------
				List[str]
					Una lista di stringhe contenente le definizioni dei metodi presenti
					all' interno della classe associata
		"""
		pass