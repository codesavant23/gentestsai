from typing import Dict, Set, Tuple, Any
from abc import abstractmethod
from .._a_platspec_cfgvalidator import _APlatSpecConfigValidator

from ...exceptions import InvalidConfigValueError



class AModelsConfigValidator(_APlatSpecConfigValidator):
	"""
		Rappresenta un `IConfigValidator` per il file di configurazione che elenca i Large Language Models
		usati nella valutazione di generazione e correzione dei tests.
		
		Il file di configurazione letto è un dizionario contenente:
		
			-   Un entry dizionario per ogni modello la cui chiave è il nome del modello.
				Il dizionario contiene, opzionalmente:
			
					* "temperature" (float): Il valore per il parametro "Temperatura" per quel modello
					* "gen_seed" (int): Il valore del seed di generazione per quel modello
					* "top-k" (int): Il valore del parametro "Top-K" per quel modello
					* "top-p" (float): Il valore del parametro "Top-P" per quel modello
					* "context_window" (int): Il valore per la grandezza della finestra di contesto di quel modello
					* "think" (bool): Il valore che specifica se usare il thinking del modello (in caso lo abbia)
					* Le altre chiavi dipendono dalla piattaforma di inferenza specifica a cui è relativo
				
		La piattaforma di inferenza specifica è descritta dai discendenti di questa classe astratta
	"""
	
	_OPT_FIELDS_NOPLAT: Set[str] = {
		"temperature", "gen_seed",
		"top-k", "top-p",
		"context_window",
		"think",
	}
	
	def __init__(
			self,
			config_dict: Dict[str, Any]
	):
		"""
			Costruisce un nuovo AModelsConfigValidator fornendogli il dizionario Python
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
	
	
	def _ap__fields(self) -> Tuple[Set[str], Set[str]]:
		return (set(), set())
	
	
	def _p__efields_strict(self) -> bool:
		return False
	
	
	def _ap__assert_mandatory(self, config_read: Dict[str, Any]):
		return
	
	
	def _ap__assert_optional(self, config_read: Dict[str, Any]):
		temp: float
		gen_seed: int
		top_k: int
		top_p: float
		ctx_window: int
		think: bool
		
		for llm_name, llm_params in config_read.items():
			temp = llm_params.get("temperature", None)
			self._pf__assert_validtype("temperature", temp, float, llm_name)
			
			gen_seed = llm_params.get("gen_seed", None)
			self._pf__assert_validtype("gen_seed", gen_seed, int, llm_name)
			
			top_k = llm_params.get("top-k", None)
			self._pf__assert_validtype("top-k", top_k, int, llm_name)
			
			top_p = llm_params.get("top-p", None)
			self._pf__assert_validtype("top-p", top_p, float, llm_name)
			
			ctx_window = llm_params.get("context_window", None)
			self._pf__assert_validtype("context_window", ctx_window, int, llm_name)
			
			think = llm_params.get("think", None)
			self._pf__assert_validtype("think", think, bool, llm_name)
	
	
	def _ap__assert_purperrors(self, config_read: Dict[str, Any]):
		return
	
	
	def _pf__assert_validtype(
			self,
			param_name: str,
			param: Any,
			expected_type: type,
			model_name: str,
	):
		"""
			Verfica se un parametro di un modello è del tipo corretto.
			
			Se la verifica ha successo quest' operazione è equivalente ad una no-op
			
			Parameters
			----------
				param_name: str
					Una stringa contenente il nome del parametro nel dizionario Python di configurazione
			
				param: Any
					Un valore qualsiasi rappresentante il parametro di cui testare
					il tipo
					
				expected_type: type
					Un tipo rappresentante il tipo previsto del parametro fornito
					
				model_name: str
					Una stringa contenente il nome del modello a cui appartiene il parametro
		"""
		if (param is not None) and (not isinstance(param, expected_type)):
			raise InvalidConfigValueError(
				f"Il tipo del parametro {param_name} è invalido (contenuto nel modello {model_name})"
			)
	
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	
	
	@abstractmethod
	def _ap__assert_platspec(self, config_read: Dict[str, Any]):
		pass
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================