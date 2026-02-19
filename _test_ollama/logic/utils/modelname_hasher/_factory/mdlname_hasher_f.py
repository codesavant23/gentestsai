from logic.utils.modelname_hasher import IModelNameHasher
from .e_hash_alg import EHashingAlgorithm

from .._private.sha256_mdlname_hasher import Sha256ModelNameHasher



class ModelNameHasherFactory:
	"""
		Rappresenta una factory per ogni `ModelNameHasherFactory`
	"""
		
	
	@classmethod
	def create(
			cls,
			algorithm: EHashingAlgorithm
	) -> IModelNameHasher:
		"""
			Istanzia un nuovo hasher di nomi di modelli che utilizza l' algoritmo di hashing richiesto
			
			Parameters
			----------
				algorithm: EHashingAlgorithm
					Un valore `EHashingAlgorithm` rappresentante l' algoritmo di hashing richiesto
					per l' oggetto `IModelNameHasher`
					
			Returns
			-------
				IModelNameHasher
					Un oggetto `IModelNameHasher` che permette di generare un digest dal nome di un LLM
					tramite l' algoritmo di hashing richiesto
		"""
		obj: IModelNameHasher
		match algorithm:
			case EHashingAlgorithm.SHA_256:
				obj = Sha256ModelNameHasher()
			
		return obj
		
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================