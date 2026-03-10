from enum import (
	Enum as PythonEnumerator,
	auto
)



class EModelCombo(PythonEnumerator):
	"""
		Rappresenta una combinazione di 1 o più Large Language Models supportata da GenTestsAI
		e compatibili, tra di loro, per determinate caratteristiche
	"""
	QWEN3_32B_Q4_K_M = auto(),
	DEEPSEEK_CODER_33B_Q4_0 = auto()