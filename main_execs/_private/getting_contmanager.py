# ============== OS Utilities ============== #
from os import environ as os_getenv
# ========================================== #
# ============== Docker SDK Utilities =============== #
from docker import (
	from_env as docker_getclient,
	DockerClient
)
# =================================================== #



def retrieve_contmanager() -> DockerClient:
	"""
		Recupera il manager degli ambienti di containerizzazione
		voluto dall' utente.
		
		Se esiste la variabile d' ambiente `DOCKER_HOST` utilizza la socket
		specificata in essa come endpoint
	"""
	cont_manager: DockerClient
	
	try:
		docker_host: str = os_getenv["DOCKER_HOST"]
		cont_manager = DockerClient(base_url=docker_host)
	except KeyError:
		cont_manager = docker_getclient()
		
	return cont_manager