class GenerationInProgressError(Exception):
	"""
		Rappresenta un' eccezione (non-exiting) che si verifica quando si richiede
		che non sia stata iniziata nessuna serie di tentativi di generazione mentre,
		invece, se ne trova una già in corso
	"""
	pass