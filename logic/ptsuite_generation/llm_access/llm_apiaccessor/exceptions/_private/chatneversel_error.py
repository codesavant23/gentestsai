class ChatNeverSelectedError(Exception):
	"""
		Rappresenta un' eccezione (non-exiting) che si verifica quando viene
		chiamata un' operazione senza aver mai impostato un oggetto chat richiesto
	"""
	pass