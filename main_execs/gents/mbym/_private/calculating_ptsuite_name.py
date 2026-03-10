def calculate_ptsuite_name(
		entity_name: str,
		prefix: str = "",
) -> str:
	"""
		Calcola il nome del file di una test-suite parziale
		
		Parameters
		----------
			entity_name: str
				Una stringa contenente il nome dell' entità di cui calcolare il nome del file
				della test-suite parziale
				
			prefix: str
				Opzionale. Default = `""`. Una stringa contenente l' eventuale prefisso da
				aggiungere al nome del file della test-suite parziale
				
		Returns
		-------
			str
				Una stringa contenente il nome del file della test-suite parziale
	"""
	return f"tests__{prefix}{entity_name}.py"