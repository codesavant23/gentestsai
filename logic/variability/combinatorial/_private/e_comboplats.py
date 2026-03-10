from enum import (
	Enum as PythonEnumerator,
	auto
)



class EPlatformCombo(PythonEnumerator):
	"""
		Rappresenta una combinazione di 1 o più piattaforme di inferenza supportata da GenTestsAI
		e compatibili, tra di loro, per determinate caratteristiche
	"""
	OLLAMA = auto(),