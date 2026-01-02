from typing import List, Dict, Set, Any
from .. import AJsonConfigReader

from ..exceptions import (
	WrongConfigFileFormatError,
	FieldDoesntExistsError
)



class GeneralJsonConfigReader(AJsonConfigReader):
	"""
		Rappresenta un `AJsonConfigReader` per il file di configurazione che specifica i parametri comuni all' intero
		software di GenTestsAI.
		
		Il file di configurazione letto sarà composto da un dizionario contenente:
			- Gli stessi campi come letti nel file di configurazione
			
	"""
	
	_ALL_FIELDS: Set[str] = {
		"default_model_params", "max_gen_times", "max_corr_times",
		"gen_tests_dir", "skipped_tests",
		"always_excluded"
	}
	_LLM_FIELDS: Set[str] = {"options", "context_window"}
	_SKIPD_FIELDS: Set[str] = {
		"file_format",
		"functions", "methods", "correction"
	}
	
	def __init__(
			self,
			file_path: str
	):
		"""
			Costruisce un nuovo GeneralJsonConfigReader fornendogli la path del file di configurazione
			che verrà associato a questo lettore.
			
			Il formato del file deve essere un dizionario JSON composto dai seguenti campi::
			
				{
					"default_model_params": {
						"context_window": <context_window>,
						"options": {
							<ollama_options>
						}
					},
					"max_gen_times": <max_generation_times>,
					"max_corr_times": <max_correction_times>,
				    "gen_tests_dir": "<generated_tests_dirname>",
					"skipped_tests": {
						"file_format": "<file_format>",
						"functions": "<funcs_skipped_filename>",
						"methods": "<meths_skipped_filename>",
						"correction": "<correction_skipped_filename>"
					}
					"always_excluded": [
						"__init__.py"
					]
				}
			
			Parameters
			----------
				file_path: str
					Una stringa rappresentante la path assoluta contenente il file di configurazione
					da associare e leggere
			
			Raises
			------
				ValueError
					Si verifica se:
					
						- La path del file di configurazione fornita ha valore `None`
						- La path del file di configurazione fornita è una stringa vuota
						
				WrongConfigFileTypeError
					Si verifica se:
						
						- Il file di configurazione dato non è un file JSON
						- Il file non è un file JSON valido
					
				InvalidConfigFilepathError
					Si verifica se:
					
						- La path del file di configurazione fornita risulta invalida sintatticamente
						- Non è possibile aprire il file di configurazione
		"""
		super().__init__(file_path)
		
		self._llm_params: Dict[str, Any] = None
		self._max_gen: int = -1
		self._max_corr: int = -1
		self._gentests_dirname: str = None
		self._skipd_tests: Dict[str, str] = None
		self._alw_excl: List[str] = None
	
	
	def _ap__assert_fields(
			self,
			config_read: Dict[str, Any]
	):
		config_fields: Set[str] = set(config_read.keys())
		if self._ALL_FIELDS > config_fields:
			raise FieldDoesntExistsError()
		
		extra_fields: Set[str] = (
			config_fields.difference(self._ALL_FIELDS).union(
			self._ALL_FIELDS.difference(config_fields))
		)
		if extra_fields != set():
			raise WrongConfigFileFormatError()
		
		self._llm_params = config_read["default_model_params"]
		self._max_gen = config_read["max_gen_times"]
		self._max_corr = config_read["max_corr_times"]
		self._gentests_dirname = config_read["gen_tests_dir"]
		self._skipd_tests = config_read["skipped_tests"]
		self._alw_excl = config_read["always_excluded"]
		
		self._assert_llm_params()
		self._assert_int(self._max_gen)
		self._assert_int(self._max_corr)
		self._assert_skipped_tests()
	
	
	def _ap__format_result(
			self,
			config_read: Dict[str, Any]
	) -> Dict[str, Any]:
		return config_read
	

	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	def _assert_llm_params(self):
		"""
			Verifica la correttezza del campo "default_model_params".
			
			Se la verifica ha successo quest' operazione è equivalente ad una no-op
			
			Raises
			------
				WrongConfigFileFormatError
					Si verifica se il formato del campo non è corretto
		"""
		llm_params_fields: Set[str] = set(self._llm_params.keys())
		if llm_params_fields != self._LLM_FIELDS:
			raise WrongConfigFileFormatError()
		
		ctx_window: int = self._llm_params["context_window"]
		model_options: Dict[str, Any] = self._llm_params["options"]
		
		self._assert_int(ctx_window)
		if "num_ctx" in model_options.keys():
			raise WrongConfigFileFormatError()


	@classmethod
	def _assert_int(
			cls,
			integer: int
	):
		"""
			Verifica la correttezza di un intero.
			
			Se la verifica ha successo quest' operazione è equivalente ad una no-op
			
			Raises
			------
				WrongConfigFileFormatError
					Si verifica se il valore intero fornito è negativo o nullo
		"""
		if integer <= 0:
			raise WrongConfigFileFormatError()


	def _assert_skipped_tests(self):
		"""
			Verifica la correttezza del campo "skipped_tests".
			
			Se la verifica ha successo quest' operazione è equivalente ad una no-op
			
			Raises
			------
				WrongConfigFileFormatError
					Si verifica se il formato del campo non è corretto
		"""
		if set(self._skipd_tests.keys()) != self._SKIPD_FIELDS:
			raise WrongConfigFileFormatError