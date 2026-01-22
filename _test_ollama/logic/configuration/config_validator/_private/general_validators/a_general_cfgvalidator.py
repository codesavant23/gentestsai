from typing import List, Dict, Set, Tuple, Any
from abc import abstractmethod
from .._a_platspec_cfgvalidator import _APlatSpecConfigValidator

from ...exceptions import InvalidConfigValueError



class AGeneralConfigValidator(_APlatSpecConfigValidator):
	"""
		Rappresenta un `IConfigValidator` per il file di configurazione che specifica i parametri
		comuni all' intero software di GenTestsAI.
		
		Il file di configurazione letto è un dizionario contenente:
		
			- "default_model_params" (Dict[str, Any]): Dizionario dei parametri di default (fallback) per i LLMs. Contiene:
			
				* "temperature" (float): Il valore di fallback per il parametro "Temperatura"
				* "gen_seed" (int): Il valore di fallback del seed di generazione
				* "top-k" (int): Il valore di fallback del parametro "Top-K"
				* "top-p" (float): Il valore di fallback del parametro "Top-P"
				* "context_window" (int): Il valore di fallback per la grandezza della finestra di contesto
				* "think" (bool): Il valore di fallback che specifica se usare il thinking del modello (in caso lo abbia)
				* Le altre chiavi dipendono dalla piattaforma di inferenza specifica a cui è relativo
				
			- "max_gen_times" (int): Numero massimo di tentativi di generazione di una test-suite parziale
			- "max_corr_times" (int): Numero massimo di tentativi di correzione di una test-suite parziale
			- "gen_tests_dir" (str): Nome della directory, nella Full Project Root Path, che conterrà i tests generati dai LLMs
			- "skipped_tests" (Dict[str, str]): Dizionario dei parametri rigurdanti eventuali tests saltati. Contiene:
			
				* "file_format" (str): Formato (es. JSON, XMLv2, YAML) dei files dei tests saltati (in minuscolo)
				* "funcs_gen" (str): Nome del file che contiene elenca le funzioni saltate durante la generazione
				* "meths_gen" (str): Nome del file che contiene elenca i metodi saltati durante la generazione
				* "funcs_corr" (str): Nome del file che elenca le funzioni saltati durante la correzione
				* "funcs_corr" (str): Nome del file che elenca i metodi saltati durante la correzione
				
			- "always_excluded" (List[str]): La lista di files, o directories, da non considerare nell' intero processo di GenTestsAI
			
		La piattaforma di inferenza specifica è descritta dai discendenti di questa classe astratta
	"""
	
	_ALL_FIELDS_NOPLAT: Set[str] = {
		"default_model_params",
		"max_gen_times", "max_corr_times",
		"skipped_tests",
		"gen_tests_dir",
		"always_excluded"
	}
	_LLM_FIELDS: Set[str] = {
		"temperature", "gen_seed",
		"top-k", "top-p",
		"context_window",
		"think",
	}
	_SKIPD_FIELDS: Set[str] = {
		"file_format",
		"funcs_gen", "meths_gen",
		"funcs_corr", "meths_corr"
	}
	
	def __init__(
			self,
			config_dict: Dict[str, Any]
	):
		"""
			Costruisce un nuovo AGeneralConfigValidator fornendogli il dizionario Python
			di configurazione che verrà associato a questo validatore
			
			Parameters
			----------
				config_dict: Dict[str, Any]
					Un dizionario variegato, indicizzato da stringhe, rappresentante il file di
					configurazione letto.
			
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il dizionario fornito ha valore `None`
						- Il dizionario fornito è vuoto
		"""
		super().__init__(config_dict)
		
		self._llm_params: Dict[str, Any] = None
		self._max_gen: int = -1
		self._max_corr: int = -1
		self._gentests_dirname: str = None
		self._skipd_tests: Dict[str, str] = None
		self._alw_excl: List[str] = None
	
	
	def _ap__fields(self) -> Tuple[Set[str], Set[str]]:
		return (self._ALL_FIELDS_NOPLAT, set())
	
	
	def _ap__assert_mandatory(
			self,
			config_read: Dict[str, Any]
	):
		key: Any
		
		def_params: Any = config_read["default_model_params"]
		if not isinstance(def_params, dict):
			raise InvalidConfigValueError('Il campo "default_model_params" non è un dizionario')
		for key in set(def_params.keys()):
			if not isinstance(key, str):
				raise InvalidConfigValueError(
					'Le chiavi del campo-dizionario "default_model_params" non sono stringhe'
				)
			
		self._assert_llm_params(def_params)
		
		max_gens: int = config_read["max_gen_times"]
		max_corrs: int = config_read["max_corr_times"]
		gen_dirname: str = config_read["gen_tests_dir"]
		
		if (
				(not isinstance(max_gens, int)) or
				(not isinstance(max_corrs, int)) or
				(not isinstance(gen_dirname, str))
		):
			raise InvalidConfigValueError()
		if (
				(max_gens <= 0) or (max_corrs <= 0) or
				(gen_dirname != "")
		):
			raise InvalidConfigValueError()
		
		skipd_tests: Dict[str, str] = config_read["skipped_tests"]
		if not isinstance(skipd_tests, dict):
			raise InvalidConfigValueError()
		self._assert_skipped_tests(skipd_tests)
		
		always_excl: List[str] = config_read["always_excluded"]
		if not isinstance(always_excl, list):
			raise InvalidConfigValueError()
		for elem in always_excl:
			if not isinstance(elem, str):
				raise InvalidConfigValueError()
	
	
	def _ap__assert_optional(self, config_read: Dict[str, Any]):
		return
	
	
	def _ap__assert_purperrors(self, config_read: Dict[str, Any]):
		return
	
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	
	
	@abstractmethod
	def _ap__assert_platspec(self, config_read: Dict[str, Any]):
		pass
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	@classmethod
	def _assert_llm_params(
			cls,
			llm_params: Dict[str, Any]
	):
		"""
			Verifica la correttezza del campo "default_model_params".
			
			Se la verifica ha successo quest' operazione è equivalente ad una no-op
			
			Raises
			------
				InvalidConfigValueError
					Si verifica se i valori dei suoi campi non sono corretti
		"""
		llm_params_fields: Set[str] = set(llm_params.keys())
		if llm_params_fields < cls._LLM_FIELDS:
			raise InvalidConfigValueError()
		
		ctx_window: int = llm_params["context_window"]
		temp: float = llm_params["temperature"]
		top_k: int = llm_params["top-k"]
		top_p: float = llm_params["top-p"]
		gen_seed: int = llm_params["gen_seed"]
		think: bool = llm_params["think"]
		
		if (
				(not isinstance(ctx_window, int)) or
				(not isinstance(temp, float)) or
				(not isinstance(top_k, int)) or
				(not isinstance(top_p, float)) or
				(not isinstance(gen_seed, int)) or
				(not isinstance(think, bool))
		):
			raise InvalidConfigValueError()
		if (
				(ctx_window <= 0) or (top_k <= 0) or
				(gen_seed < 0) or
				(not (0.0 <= top_p <= 1.0)) or
				(not (0.0 <= temp <= 1.0))
		):
			raise InvalidConfigValueError()
		

	@classmethod
	def _assert_skipped_tests(
			cls,
			skipd_tests: Dict[str, str]
	):
		"""
			Verifica la correttezza del campo "skipped_tests".
			
			Se la verifica ha successo quest' operazione è equivalente ad una no-op
			
			Raises
			------
				WrongConfigFileFormatError
					Si verifica se il formato del campo non è corretto
		"""
		for key, value in skipd_tests.items():
			if not isinstance(key, str) or not isinstance(value, str):
				raise InvalidConfigValueError()
		
		if set(skipd_tests.keys()) != cls._SKIPD_FIELDS:
			raise InvalidConfigValueError()