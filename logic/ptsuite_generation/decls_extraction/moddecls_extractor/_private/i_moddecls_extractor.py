from typing import List
from abc import ABC, abstractmethod

from ...classdecls_extractor import IClassDeclsExtractor



class IModuleDeclsExtractor(ABC):
	"""
		Rappresenta un oggetto in grado di estrarre le dichiarazioni di un module-file Python associato
		separandone le funzioni dalle classi che si trovano in esso.
		
		La tecnologia implementativa utilizzata è specificata dai discendenti di questa interfaccia.
	"""


	@abstractmethod
	def extract_funcs(self) -> List[str]:
		"""
			Estrae i nomi delle funzioni definite all' interno del module-file associato
			
			Returns
			-------
				List[str]
					Una lista di stringhe contenente i nomi delle funzioni definite
					nel namespace del modulo
		"""
		pass
	
	
	@abstractmethod
	def extract_classes(self) -> List[IClassDeclsExtractor]:
		"""
			Estrae dal module-file impostato le classi che sono definite nel suo namespace
			
			Returns
			-------
				List[IClassDeclsExtractor]
					Una lista di oggetti `IClassDeclsExtractor`, uno per ogni classe definita
					nel module-file
		"""
		pass