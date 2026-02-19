from abc import abstractmethod
from .. import IModelNameHasher



class _ABaseModelNameHasher(IModelNameHasher):
	"""
		Rappresenta un `IModelNameHasher` di base, ovvero che contiene la logica
		comune ad ogni `IModelNameHasher`
		
		L' algoritmo di hashing utilizzato specificato dai discendenti di questa classe astratta
	"""
	
	
	def hash_name(
			self,
			model_name: str,
			chars: int = -1
	) -> str:
		if (model_name is None) or (model_name == ""):
			raise ValueError()
		
		max_chars: int = self._ap__alg_maxchars()
		wnted_chars: int
		if chars == -1:
			wnted_chars = max_chars
		else:
			wnted_chars = chars
			
		return self._ap__hash_name_spec(model_name, wnted_chars)


	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	
	
	@abstractmethod
	def _ap__alg_maxchars(self) -> int:
		"""
			Restituisce il numero di caratteri massimi dell' algoritmo di hashing
			specificato dai discendenti di questa classe astratta
			
			Returns
			-------
				int
					Un intero che indica da quanti caratteri sono composti i digest
					dell' algoritmo specificato dai discendenti di questa classe astratta
		"""
		pass
	
	
	@abstractmethod
	def _ap__hash_name_spec(
			self,
			model_name: str,
			chars: int
	) -> str:
		"""
			Effettua l' hashing del nome del modello fornito restituendo il numero
			di caratteri desiderati.
			
			E' garantito all' interno di questo metodo:
					
					- Che `model_name` non abbia valore `None` nè sia una stringa vuota
					- Che `chars` non superi il massimo numero di caratteri del digest dell' algoritmo di hashing
			
			Parameters
			----------
				model_name: str
					Una stringa contenente il nome del modello di cui effettuare
					l' hashing
					
				chars: int
					Un intero che indica quanti caratteri restituire dell' hashing
					effettuato
					
			Returns
			-------
				str
					Una stringa rappresentante il digest, nell' algoritmo specificato dai discendenti,
					del nome del modello fornito della lunghezza di caratteri desiderata
		"""
		pass
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================