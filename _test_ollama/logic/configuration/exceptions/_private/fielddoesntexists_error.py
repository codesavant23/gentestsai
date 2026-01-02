from .. import WrongConfigFileFormatError



class FieldDoesntExistsError(WrongConfigFileFormatError):
	"""
		Rappresenta un' eccezione (non-exiting) che si verifica quando viene 
		eseguita un' operazione dandole un formato di file di configurazione
		errato che, nello specifico, ha uno o più campi obbligatori mancanti
	"""
	pass
