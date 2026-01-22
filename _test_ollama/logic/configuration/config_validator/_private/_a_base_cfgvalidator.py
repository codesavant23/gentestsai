from typing import Dict, Set, Tuple, Any
from abc import abstractmethod
from .. import IConfigValidator

from ..exceptions import (
	FieldDoesntExistsError,
	WrongConfigFileFormatError
)



class _ABaseConfigValidator(IConfigValidator):
	"""
		Rappresenta un `IConfigValidator` di base, ovvero che contiene la logica di controllo
		comune ad ogni `IConfigValidator`.
		
		Lo scopo del file di configurazione validato è specificato dai discendenti di questa
		classe astratta.
	"""
	
	def __init__(
			self,
			config_dict: Dict[str, Any]
	):
		"""
			Costruisce un nuovo _ABaseConfigReader fornendogli il dizionario Python di configurazione
			che verrà associato a questo validatore
			
			Parameters
			----------
				config_dict: Dict[str, Any]
					Un dizionario variegato, indicizzato da stringhe, rappresentante il file di
					configurazione letto
			
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il dizionario fornito ha valore `None`
						- Il dizionario fornito è vuoto
		"""
		if config_dict is None:
			raise ValueError()
		if len(config_dict) == 0:
			raise ValueError()
		
		self._dict: Dict[str, Any] = config_dict
	
	
	def validate_sem(self):
		config_fields: Set[str] = set(self._dict.keys())
		mand_fields, opt_fields = self._ap__fields()
		
		has_all_mands: bool = (
			len(config_fields.intersection(mand_fields)) == len(mand_fields)
		)
		if not has_all_mands:
			raise FieldDoesntExistsError()
		
		if self._p__efields_strict():
			all_fields: Set[str] = mand_fields.union(opt_fields)
			has_extra_fields: bool = config_fields.difference(all_fields) != set()
			if has_extra_fields:
				raise WrongConfigFileFormatError()
		
		self._ap__assert_mandatory(self._dict)
		self._ap__assert_optional(self._dict)
		self._ap__assert_purperrors(self._dict)
		
		
	def _pf__get_dict(self) -> Dict[str, Any]:
		"""
			Restituisce il dizionario Python di configurazione
		"""
		return self._dict
	
	
	def _p__efields_strict(self) -> bool:
		"""
			Indica se è necessario effettuare il controllo degli extra fields
			oppure saltarlo.
			Si utilizza, ad esempio, in casi in cui il file di configurazione non ha
			campi fissi.
			
			Se non è ovverridato questo metodo restituisce `True`.
			
			Returns
			-------
				bool
					Un booleano indicante se effettuare il controllo degli extra fields
		"""
		return True
	
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	
	
	@abstractmethod
	def _ap__fields(self) -> Tuple[Set[str], Set[str]]:
		"""
			Restituisce i campi obbligatori, e opzionali, (entrambi al 1° livello del dizionario)
			di cui, rispettivamente, deve e può essere composto il file di configurazione
			che va validato
			
			Returns
			-------
				Tuple[Set[str], Set[str]]
					Una tupla di insiemi di stringhe rappresentanti:
					
						- [0]: L' insieme dei nomi dei campi obbligatori
						- [1]: L' insieme dei nomi dei campi opzionali
		"""
		pass
	
	
	@abstractmethod
	def _ap__assert_mandatory(
			self,
			config_read: Dict[str, Any]
	):
		"""
			Controlla la validità dei valori dei campi obbligatori contenuti nel file
			di configurazione che è stato fornito.
			
			Se la validazione va a buon fine quest' operazione deve essere equivalente ad una no-op.
			
			E' garantito all' interno di questo metodo:
			
				- Che tutti i campi obbligatori esistano (al 1° livello del dizionario)
				- Che non ci siano campi non voluti, se richiesto (al 1° livello del dizionario)
				
			Parameters
			----------
				config_read: Dict[str, Any]
					Un dizionario variegato, indicizzato da stringhe, rappresentante il file di
					configurazione letto
		
			Raises
			------
				InvalidConfigValueError
					Si verifica se la semantica di uno o più campi obbligatori è errata
		"""
		pass
	
	
	@abstractmethod
	def _ap__assert_optional(
			self,
			config_read: Dict[str, Any]
	):
		"""
			Controlla la validità dei valori dei campi opzionali contenuti nel file
			di configurazione che è stato fornito.
			
			Se la validazione va a buon fine quest' operazione deve essere equivalente ad una no-op.
			
			E' garantito all' interno di questo metodo:
			
				- Che tutti i campi obbligatori esistano e siano semanticamente corretti
				- Che non ci siano campi non voluti, se richiesto (al 1° livello del dizionario)
				
			Parameters
			----------
				config_read: Dict[str, Any]
					Un dizionario variegato, indicizzato da stringhe, rappresentante il file di
					configurazione letto
		
			Raises
			------
				WrongConfigFileFormatError
					Si verifica se il file di configurazione contiene campi non previsti dallo scopo
					specificato dai discendenti di questa classe astratta
			
				InvalidConfigValueError
					Si verifica se la semantica di uno o più campi opzionali è errata
		"""
		pass
	
	
	@abstractmethod
	def _ap__assert_purperrors(
			self,
			config_read: Dict[str, Any]
	):
		"""
			Controlla eventuali errori relativi allo scopo specificato dai discendenti di
			questa classe astratta.
			
			Se la validazione va a buon fine quest' operazione deve essere equivalente ad una no-op.
			
			E' garantito all' interno di questo metodo:
			
				- Che tutti i campi obbligatori esistano e siano semanticamente corretti
				- Che i campi opzionali, che esistono, siano semanticamente corretti

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
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================