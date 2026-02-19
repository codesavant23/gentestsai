from abc import ABC, abstractmethod



class IModelNameHasher(ABC):
	"""
		Rappresenta un oggetto capace di hashare il nome di una specifica implementazione
		di un Large Language Model.
		
		L' algoritmo di hashing utilizzato è specificato dai discendenti di questa interfaccia
	"""


	@abstractmethod
	def hash_name(self, model_name: str, chars: int = -1) -> str:
		"""
			Effettua l' hashing del nome del modello fornito restituendo il numero
			di caratteri desiderati.
			
			Parameters
			----------
				model_name: str
					Una stringa contenente il nome del modello di cui effettuare
					l' hashing
					
				chars: int
					Opzionale. Default = `-1`. Un intero che indica quanti caratteri
					restituire dell' hashing effettuato.
					Se si fornisce `-1`, o non si fornisce il parametro, si restituiranno
					tutti i caratteri del digest prodotto
					
			Returns
			-------
				str
					Una stringa rappresentante il digest, nell' algoritmo specificato dai discendenti,
					del nome del modello fornito della lunghezza di caratteri desiderata
					
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il parametro `model_name` ha valore `None`
						- Il parametro `model_name` è una stringa vuota
		"""
		pass