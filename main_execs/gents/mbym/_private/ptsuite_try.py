class PtsuitePromptingTry:
	"""
		Rappresenta un tentativo di prompting effettuato, per la generazione o correzione,
		di una test suite parziale
	"""
	
	def __init__(self):
		"""
			Crea un nuovo PtsuitePromptingTry
		"""
		self._ptsuite: str = ""
		self._try: int = -1
	
	
	def set_ptsuite(self, ptsuite_code: str):
		"""
			Imposta la test suite parziale del tentativo
			
			Parameters
			----------
				ptsuite_code: str
					Una stringa rappresentante la test suite parziale da impostare
					come nuova test suite parziale del nuovo tentativo
					
			Raises
			------
				ValueError
					Si verifica se `ptsuite_code` ha valore `None`
		"""
		if ptsuite_code is None:
			raise ValueError()
		
		self._ptsuite = ptsuite_code
		
		
	def get_ptsuite(self) -> str:
		"""
			Restituisce la test suite parziale del tentativo
			
			Returns
			-------
				str
					Una stringa rappresentante la test suite parziale impostata
					nel tentativo di prompting
		"""
		return self._ptsuite
	
	
	def set_try(self, try_num: int):
		"""
			Imposta il numero di tentativo del tentativo di prompting
			
			Parameters
			----------
				try_num: int
					Un intero contenente il numero di tentativo da impostare
					come nuovo numero del nuovo tentativo di prompting
					
			Raises
			------
				ValueError
					Si verifica se `try_num` è minore di 0
		"""
		if try_num < 0:
			raise ValueError()
		
		self._try = try_num
		
		
	def get_try(self) -> str:
		"""
			Restituisce la test suite parziale del tentativo
			
			Returns
			-------
				int
					Un intero contenente il numero di tentativo da impostare
					come nuovo numero del nuovo tentativo di prompting
		"""
		return self._ptsuite