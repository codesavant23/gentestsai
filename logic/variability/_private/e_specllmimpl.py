from enum import (
	Enum as PythonEnumerator,
	auto
)



class ESpecLlmImpl(PythonEnumerator):
	"""
		Rappresenta una specifica implementazione di un LLM
	"""
	QWEN3_32B_Q4_K_M = auto(),
	DEEPSEEK_CODER_33B_Q4_0 = auto(),