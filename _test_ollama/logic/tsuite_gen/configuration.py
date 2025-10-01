from typing import Dict, List, Any

from base64 import b64encode as b64_encode

from json import loads as json_loads
from os.path import (
	join as path_join
)

from re import search as reg_search

from httpx import Timeout as HttpxTimeout

from _test_ollama.logic.utils.json_to_str import (
	read_json_tobuff
)

MODEL_PATT: str = r"^[a-zA-z0-9\.\-_]+(?:\:[a-zA-z0-9\.\-_]+)?$"



def configure_ollama(
		api_url: str,
		userpass_pair: str,
		llm_model: str,
		conn_timeout: str,
		resp_timeout: str,
		dict_to_use: Dict[str, Any]=None
) -> Dict[str, Any]:
	"""
		<Descrizione>

		Parameters
		----------
		api_url: str
			Una stringa contenente l' URL (URI:Port) a cui è hostata l' istanza di Ollama con cui si effettueranno le
			interazioni

		userpass_pair: str
			Una stringa contenente la coppia username e password (User:Pass) utilizzati come credenziali di

		llm_model: str
			Una stringa contenente la coppia "modello:implementazione"

		dict_to_use: Dict[str, Any]
			Opzionale. Il dizionario variegato, indicizzato su stringhe, da completare con la configurazione di Ollama
			senza creare un nuovo dizionario di configurazione

		Returns
		-------
		Dict[str, Any]
			Un dizionario variegato, indicizzato su stringhe, contenente:

				- "model" (str): Il modello da utilizzare
				- "api_url" (str): L' URL per l' accesso alla specifica istanza di Ollama hostata
							utilizzata dallo script.
				- "api_auth" (str): Le credenziali di autorizzazione codificate e utilizzabili
							 per accedere all' API di Ollama (da utilizzarsi come valore
							 dell' header "Authorization")
				- "timeout" (httpx.Timeout): L' oggetto Timeout da utilizzare per la creazione dell'
											 oggetto Client di Ollama
				- ed, eventualmente, se `dict_to_use` non è `None` anche le sue chiavi e i suoi valori

	"""
	if reg_search(MODEL_PATT, llm_model) is None:
		raise ValueError("La coppia modello:tag data è malformata o invalida")

	config: Dict[str, Any]
	if dict_to_use is not None:
		config = dict_to_use
	else:
		config = dict()

	config["api_url"] = "http://" + api_url
	config["api_auth"] = f'Basic {b64_encode(userpass_pair.encode()).decode()}'

	config["model"] = llm_model

	conn_timeout_float: float = int(conn_timeout) / 1000.0
	resp_timeout_float: float = int(resp_timeout) / 1000.0
	config["timeout"] = HttpxTimeout(
		connect=conn_timeout_float,
		read=resp_timeout_float,
		write=None,
		pool=None
	)

	return config


def read_gentests_conf(
		config_path: str
) -> Dict[
		str,
		Any
	]:
	"""
		Legge la configurazione dei parametri necessari alla generazione completa di tutti i tests

		Returns
		-------
		Dict[str, Any]
			Un dizionario, indicizzato su stringhe, contenente:

				- "general_config" (Dict[str, Any]): La configurazione di parametri generali utilizzati dal progetto
				- "projs_config" (Dict[str, Dict[str, Any]]): La configurazione contenente le informazioni relative ai progetti focali
				- "ollama_config" (Dict[str, str]): La configurazione di informazioni per l' autenticazione con l' applicativo Ollama
				- "models_config" (List[str]): I modelli da utilizzare per la generazione dei tests e la valutazione degli stessi
				- "prompts_config" (Dict[str, str]): La configurazione dei nomi dei files relativi ai Template Prompt da utilizzare
	"""
	general_config: Dict[str, Any] = json_loads(
		read_json_tobuff(
			path_join(config_path, "general.json")
		)
	)

	projs_config: Dict[str, Dict[str, Any]] = json_loads(
		read_json_tobuff(
			path_join(config_path, "projs.json")
		)
	)

	ollamaauth_config: Dict[str, str] = json_loads(
		read_json_tobuff(
			path_join(config_path, "ollama.json")
		)
	)

	models_config: List[Dict[str, Any]] = json_loads(
		read_json_tobuff(
			path_join(config_path, "models.json")
		)
	)

	prompts_config: Dict[str, str] = json_loads(
		read_json_tobuff(
			path_join(config_path, "prompts.json")
		)
	)

	return {
		"general_config": general_config,
		"projs_config": projs_config,
		"ollama_config": ollamaauth_config,
		"models_config": models_config,
		"prompts_config": prompts_config
	}