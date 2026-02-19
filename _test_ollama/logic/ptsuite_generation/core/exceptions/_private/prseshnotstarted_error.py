class PromptingSessionNotStartedError(Exception):
	"""
		Rappresenta un' eccezione (non-exiting) che si verifica quando si richiede
		sia stata iniziata una serie di tentativi di generazione/correzione
		mentre, invece, non se ne trova una in corso
	"""
	pass