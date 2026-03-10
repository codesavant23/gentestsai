from ._a_base_mdlname_hasher import _ABaseModelNameHasher

from hashlib import sha256



class Sha256ModelNameHasher(_ABaseModelNameHasher):
	"""
		Rappresenta un `IModelNameHasher` implementato con l' algoritmo
		di hashing SHA-256
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo Sha256ModelNameHasher
		"""
		pass
	
	
	def _ap__alg_maxchars(self) -> int:
		return 64
	
	
	def _ap__hash_name_spec(
			self,
			model_name: str,
			chars: int
	) -> str:
		digest: str = sha256(model_name.encode("utf-8")).hexdigest()
		return digest[:chars]


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================