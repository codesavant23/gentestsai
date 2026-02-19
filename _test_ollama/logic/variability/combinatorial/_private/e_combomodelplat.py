from enum import (
	Enum as PythonEnumerator,
	auto
)



class EModelPlatformCombo(PythonEnumerator):
	"""
		Rappresenta una combinazione di 1 o più piattaforme di inferenza, e di 1 o più LLMs,
		supportata da GenTestsAI e compatibili, tra di loro, per determinate caratteristiche
	"""
	# Per ora non ci sono piattaforme compatibili tra di loro insieme a modelli per cui
	# si debbano avere delle entries in questo enumeratore
	
	# Si elencano prima le piattaforme, separate dal carattere "_"
	# Poi si elencano i modelli, separati dal carattere "_"
	# Piattaforme e modelli sono separate dalla stringa "__"
	pass