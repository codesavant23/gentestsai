from abc import ABC, abstractmethod



class ISkipWriter(ABC):
	"""
		Rappresenta uno scrittore di tests saltati durante la fase di generazione o correzione
		da parte di un LLM.
		
		Il tipo del file dei tests saltati è specificato dai discendenti di questa interfaccia.
		Il formato del file dei tests saltati è specificato dai discendenti di questa interfaccia.
	"""


	@abstractmethod
	def write_skipd_test(
			self,
			entity_name: str
	):
		"""
			Scrive sul file associato, dei tests saltati, che il test legato all' entità specificata
			non è andato a buon fine in una delle 2 fasi di generazione o correzione
			
			Parameters
			----------
				entity_name: str
					Una stringa contenente il nome dell' entità di codice autonoma (funzione o metodo)
					la cui generazione o correzione non è andata a buon fine
					
			Raises
			------
				ValueError
					Si verifica se la stringa data è vuota
						
				OSError
					Si verifica se non è possibile scrivere sul file associato
		"""
		pass