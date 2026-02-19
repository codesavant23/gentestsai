from typing import Tuple

# =========== ArgParse Utilities =========== #
from argparse import (
	ArgumentParser,
	Namespace as ArgumentsList,
	ZERO_OR_MORE,
	ONE_OR_MORE,
)
ARGP_0_PLUS = ZERO_OR_MORE
ARGP_1_PLUS = ONE_OR_MORE
ARGP_POS_OPT = "?"
# ========================================== #

from logic.utils.modelname_hasher import EHashingAlgorithm



def read_arguments() -> Tuple[str, EHashingAlgorithm, int]:
	"""
		Legge gli argomenti forniti alla chiamata di "exec_pdirs_hasher.py" da linea di comando
		
		Returns
		-------
			Tuple[str, EHashingAlgorithm, int]
				Una tupla mista contenente:
					
					- [0]: Il nome del modello fornito come argomento (in lowercase)
					- [1]: L' algoritmo di hashing da utilizzare
					- [2]: Il numero di caratteri da conservare del digest che verrà generato
					
		Raises
		------
			ValueError
				Si verifica se il numero di caratteri forniti è 0 o minore di -1
	"""
	arg_parser: ArgumentParser = ArgumentParser(
		description="GenTestsAI's executable for obtaining names of LLM prompt directories",
		usage="python exec_pdirs_hasher.py [-a <hashing_algorithm>] <model_name>"
	)
	
	arg_parser.add_argument(
		"-a", "--algorithm",
		help='Optional. Selected hashing algorithm',
		required=False,
		default="sha-256"
	)
	arg_parser.add_argument(
		"-c", "--chars",
		help="Optional. Number of characters desired (digest is trimmed to this length)",
		required=False,
		type=int, default=-1
	)
	arg_parser.add_argument(
		"model_name",
		help='Model name to hash'
	)
	
	args: ArgumentsList = arg_parser.parse_args()
	
	if (args.chars < -1) or (args.chars == 0):
		raise ValueError()
	
	model_name: str = args.model_name.lower()
	alg_str: str = args.algorithm.replace("-", "_").upper()
	algorithm: EHashingAlgorithm = EHashingAlgorithm[alg_str]
	chars: int = args.chars

	return (model_name, algorithm, chars)