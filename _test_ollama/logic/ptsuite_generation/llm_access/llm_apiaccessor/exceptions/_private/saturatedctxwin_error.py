class SaturatedContextWindowError(Exception):
	"""
		Rappresenta un' eccezione (non-exiting) che si verifica se il LLM, a cui è stato richiesto
		di generare, o correggere una test suite parziale, satura la finestra di contesto.
		E' possibile che ciò sia legato alla problematica del "Semantic Drift".
	"""
	pass