from typing import Dict, Set, Any
from .. import AJsonConfigReader

from ..exceptions import WrongConfigFileFormatError



class ModelsJsonConfigReader(AJsonConfigReader):
	"""
		Rappresenta un `AJsonConfigReader` per il file di configurazione che elenca i Large Language Models
		usati nella valutazione di generazione e correzione dei tests.
		
		Il file di configurazione letto sarà composto da un dizionario contenente:
			- Come chiavi: Il nome dei Large Language Models scelti
			- Come valori: Un dizionario Python per ogni LLM scelto vuoto o con gli stessi campi come letti nel file di configurazione
	"""
	
	_PARAM_FIELDS: Set[str] = {"context_window", "options"}
	
	def __init__(
			self,
			file_path: str
	):
		"""
			Costruisce un nuovo ModelsJsonConfigReader leggendo il file di configurazione alla path
			specificata.
			
			Il formato del file deve essere un dizionario JSON composto nel seguente modo::
			
				{
					"<model1_name>": {
						"(optional) context_window": <context_window>,
						"(optional) options": {
							<ollama_options_without_ctxwin>
						}
					},
					...
				}
			
			Parameters
			----------
				file_path: str
					Una stringa rappresentante la path assoluta contenente il file di configurazione
					da leggere
			
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
	
	
	def _ap__assert_fields(
			self,
	        config_read: Dict[str, Any]
	):
		for llm_name, llm_params in config_read.items():
			llm_params_fields = set(llm_params.keys())
			if llm_params_fields > self._PARAM_FIELDS:
				raise WrongConfigFileFormatError()
			
			llm_options: Dict[str, Any] = llm_params.get("options", None)
			llm_ctx_win: int = llm_params.get("context_window", None)
			if llm_options is not None:
				if "num_ctx" in llm_options.keys():
					raise WrongConfigFileFormatError()
			if llm_ctx_win is not None:
				if llm_ctx_win <= 0:
					raise WrongConfigFileFormatError()
	
	
	def _ap__format_result(
			self,
			config_read: Dict[str, Any]
	) -> Dict[str, Any]:
		return config_read