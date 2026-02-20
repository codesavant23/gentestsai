from logic.utils.modelname_hasher import (
	IModelNameHasher,
	ModelNameHasherFactory, EHashingAlgorithm
)



def normalize_llmname(
		model_name: str,
		algorithm: str,
		chars: int,
) -> str:
	algo_enum: EHashingAlgorithm = EHashingAlgorithm[
		algorithm.lower().upper().replace("-", "_")
	]
	
	hasher: IModelNameHasher = ModelNameHasherFactory.create(algo_enum)
	partial_digest: str = hasher.hash_name(model_name, chars)
	
	return partial_digest