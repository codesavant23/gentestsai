from typing import Dict, Set, Tuple, Any
from abc import abstractmethod
from ._a_base_cfgvalidator import _ABaseConfigValidator



class _APlatSpecConfigValidator(_ABaseConfigValidator):
	"""
		Rappresenta un `IConfigValidator` per files di configurazione il cui scopo definisce campi
		relativi a una piattaforma specifica.
		
		Lo scopo del file di configurazione validato è specificato dai discendenti di questa
		classe astratta.
		La piattaforma di inferenza specifica è descritta dai discendenti di questa classe astratta.
	"""
	
	def __init__(
			self,
			config_dict: Dict[str, Any]
	):
		"""
			Costruisce un nuovo _APlatSpecConfigValidator fornendogli il dizionario Python di configurazione
			che verrà associato a questo validatore
			
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
	
	
	def validate_sem(self):
		super().validate_sem()
		
		self._ap__assert_platspec(self._pf__get_dict())
	
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	
	
	@abstractmethod
	def _ap__assert_platspec(self, config_read: Dict[str, Any]):
		"""
			Controlla la validità dei valori dei campi relativi alla piattaforma di inferenza
			specificata dai discendenti di questa classe astratta.
			
			Se la validazione va a buon fine quest' operazione deve essere equivalente ad una no-op.
		
			E' garantito all' interno di questo metodo:
			
				- Che tutti i campi obbligatori, non specifici della piattaforma di inferenza,
				  esistano e siano semanticamente corretti
				- Che i campi opzionali, che esistono, non specifici della piattaforma di inferenza,
				  siano semanticamente corretti
				  
			Parameters
			----------
				config_read: Dict[str, Any]
					Un dizionario variegato, indicizzato da stringhe, rappresentante il file di
					configurazione letto
			
			Raises
			------
				InvalidConfigValueError
					Si verifica se la semantica di uno o più campi è corretta ma sussiste
					un errore specifico dichiarato dai discendenti di questa classe astratta
		"""
		pass
	
	
	@abstractmethod
	def _ap__fields(self) -> Tuple[Set[str], Set[str]]:
		pass
	
	
	@abstractmethod
	def _ap__assert_mandatory(self, config_read: Dict[str, Any]):
		pass
	
	
	@abstractmethod
	def _ap__assert_optional(self, config_read: Dict[str, Any]):
		pass
	
	
	@abstractmethod
	def _ap__assert_purperrors(self, config_read: Dict[str, Any]):
		pass
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================