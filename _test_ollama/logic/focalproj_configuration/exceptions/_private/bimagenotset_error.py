class BaseImageNotSetError(Exception):
	"""
		Rappresenta un' eccezione (non-exiting) che si verifica quando viene eseguita
		un' operazione che richiederebbe un' immagine base già impostata ma non è
		stata impostata alcuna
	"""
	pass