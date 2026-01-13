class ApiResponseError(Exception):
	"""
	    Rappresenta un' eccezione (non-exiting) che si verifica quando avviene
	    un errore rigurardante l' API scelta per l' interazione durante la
	    risposta di una richiesta fatta ad un LLM.
	    La natura dell' errore può essere non identificata.
	    
	    L' attirbuto `args` è valorizzato con il valore di `args` dell' eccezione
	    specifica che si è verificata con l' API (se è possibile ottenerla).
	"""
	pass