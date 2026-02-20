from typing import Tuple
from abc import abstractmethod
from .. import ISyntacticChecker



class _ABaseSyntacticChecker(ISyntacticChecker):
	"""
		Rappresenta un `ISyntacticChecker` di base ovvero che contiene la logica
		comune ad ogni `ISyntacticChecker`.
		
		Il tool di verifica è specificato dai discendenti di questa classe astratta
	"""
		
		
	def check_synt(
			self,
			ptsuite_code: str
	) -> Tuple[str, str]:
		if (ptsuite_code is None) or (ptsuite_code == ""):
			raise ValueError()
			
		return self._ap__check_synt_spec(ptsuite_code)
		
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	
	
	@abstractmethod
	def _ap__check_synt_spec(self, ptsuite_code: str) -> Tuple[str, str]:
		"""
			Effettua il controllo di correttezza sintattica della test-suite parziale
			fornita come argomento utilizzando il tool di verifica specificato
			dai discendenti di questa classe astratta.
			
			E' garantito all' interno di questo metodo che il parametro `ptsuite_code` non abbia
			valore `None` nè sia una stringa vuota
			
			Parameters
			----------
				ptsuite_code: str
					Una stringa contenente il codice della test-suite parziale di cui
					effettuare la verifica di correttezza sintattica
			
			Returns
			-------
				Tuple[str, str]
					Una tupla di 2 stringhe rappresentante l' eventuale primo errore sintattico
					della test-suite parziale. Contiene opzionalmente:
					
						- [0]: Il nome della problematica riscontrata nella verifica di correttezza effettuata
						- [1]: Il messaggio associato alla problematica riscontrata nella verifica di correttezza effettuata
						
					Se non si è verificato nessun errore viene restituita una tupla vuota
		"""
		pass


	@abstractmethod
	def clear_resources(self):
		pass


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================