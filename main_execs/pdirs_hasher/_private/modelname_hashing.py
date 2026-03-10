from main_execs.pdirs_hasher import read_arguments
from logic.utils.modelname_hasher import ModelNameHasherFactory



def hash_modelname() -> str:
	"""
		Effettua l' hashing del nome del modello fornito, utilizzando l' algoritmo
		fornito come argomento.
		
		Vengono restituiti soltanto il numero di caratteri forniti come argomento.
		Nel caso in cui il numero di caratteri non sia specificato, o viene fornito
		`-1`, vengono restituiti tutti i caratteri del digest
	"""
	model_name, algorithm, chars = read_arguments()
	
	return ModelNameHasherFactory.create(algorithm).hash_name(model_name, chars)