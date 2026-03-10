from enum import Enum as PythonEnumerator



class EContainerManager(PythonEnumerator):
	"""
		Rappresenta un "Container Manager" di cui è possibile ottenere il pulitore
		della cache di building in GenTestsAI
	"""
	DOCKER = 0,
	PODMAN_GE400 = 1
	PODMAN_LT400 = 2