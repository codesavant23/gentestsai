from typing import Dict

from io import BytesIO
from tarfile import (
	open as tarf_open,
	TarInfo
)
# ============== Docker SDK Utilities =============== #
from docker.models.images import Image as DockerImage
# =================================================== #
# ============ Path Utilities ============ #
from os.path import (
	split as path_split,
	splitext as path_splitext,
	relpath as path_relative
)
# ======================================== #
# ============== JSON Utilities ============== #
from json import JSONDecoder
# ============================================ #

from ......utils.logger import ATemporalFormattLogger
from ......utils.logger.exceptions import FormatNotSetError

from ......focalproj_configuration.focal_container import FocalContainer
from ......focalproj_configuration.focal_container.exceptions import (
	ContainerAlreadyRunningError,
	ContainerNotRunningError
)

from ..exceptions import ProjectNotSetError



class LintingChecker:
	"""
		Rappresenta un oggetto in grado di effettuare la verifica di correttezza,
		a livello di linting, di test-suites parziali tramite un tool di verifica
		installato all' interno dell' ambiente focale.
		
		Attributi di Classe Pubblici:
			- `LINTING_TEMP_DIR` (str) : Rappresenta il nome, di default, della directory temporanea, nel container, in cui verranno memorizzati i files usati temporaneamente durante la verifica del codice
			- `LINTING_SCRIPT` (str) : Rappresenta il nome, di default, dello script Python, contenuto nella directory dei tools per la verifica a livello di linting, che eseguirà la verifica nell' ambiente del progetto focale tramite gli strumenti scelti
	"""
	
	_RESULT_FNAME: str = "gtsai__linting_result.json"
	
	def __init__(
			self,
			path_prefix: str,
			fenv_script_fname: str,
			inputctr_dirname: str,
	        logger: ATemporalFormattLogger = None,
	):
		"""
			Costruisce un nuovo LintingChecker associandolo eventualmente al logger utilizzato per registrare
			gli steps di ogni verifica a livello di linting effettuata.
			
			Parameters
			----------
				path_prefix: str
					Una stringa contenente il path prefix impostato per gli ambienti focali che si
					utilizzeranno
			
				fenv_script_fname: str
					Una stringa contenente il nome dello script Python che esegue la verifica di correttezza,
					a livello di linting, all' interno dell' ambiente focale
			
				inputctr_dirname: str
					Una stringa rappresentante il nome della directory, all' interno del path prefix dell' ambiente focale,
					che conterrà la copia temporanea delle test-suites parziali di cui effettuare la verifica di linting.
			
				logger: ATemporalFormattLogger
					Opzionale. Default = `None`. Un oggetto `ATemporalFormattLogger` rappresentante l' eventuale logger
					da utilizzare per registrare le fasi di ogni tentativo di correzione (non per registrare le fasi
					della richiesta al LLM)
					
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il parametro `path_prefix` ha valore `None`
						- Il parametro `path_prefix` è una stringa vuota
						- Il parametro `fenv_script_fname` ha valore `None`
						- Il parametro `fenv_script_fname` è una stringa vuota
						- Il parametro `shared_dirname` ha valore `None`
						- Il parametro `shared_dirname` è una stringa vuota
		"""
		if(path_prefix is None) or (path_prefix == ""):
			raise ValueError()
		if(fenv_script_fname is None) or (fenv_script_fname == ""):
			raise ValueError()
		if(inputctr_dirname is None) or (inputctr_dirname == ""):
			raise ValueError()
		
		self._focal_env: FocalContainer = None
		
		# Attributi relativi al progetto focale impostato
		self._proj_name: str = None
		self._full_root: str = None
		self._focal_env: FocalContainer = None
		
		# Nome dello script Python che esegue il linter all' interno dell' ambiente focale
		self._fenv_script_fname: str = fenv_script_fname
		
		# Il path prefix (o path principale) di ogni ambiente focale
		self._path_prefix: str = path_prefix
		# Nome della directory che conterrà le test-suites parziali di cui effettuare la verifica
		self._input_dir: str = inputctr_dirname
		
		# Path (reale) del risultato della verifica di linting effettuata
		self._lint_result_path: str = None
		# Path (relativa) del file con la test-suite parziale per la verifica di linting
		self._ptsuite_relpath: str = f"{self._input_dir}/temp_ptsuite.py"
		# Path (relativa) del risultato della verifica di linting effettuata da un singolo tentativo
		self._lint_result_relpath: str = None
		
		# Logger da utilizzare per loggare gli steps di ogni verifica
		self._logger: ATemporalFormattLogger = logger
		
		# Setup del formato del logger
		def_time_format: str = "( {day}-{month}-{year} | {hour}:{min}:{second} )"
		logger_frmt: str
		try:
			logger_frmt = self._logger.unset_format() if logger is not None else None
		except FormatNotSetError:
			logger_frmt = "[LintingChecker] {message} " + def_time_format
		self._logger.set_format(logger_frmt) if logger is not None else None
		
		self._inited: bool = False
		self._proj_set: bool = False
	
	
	def set_focal_project(
			self,
			project_name: str,
			full_root: str,
			env_image: DockerImage,
			path_prefix: str
	):
		"""
			Imposta il prossimo progetto focale delle quali test-suites parziali si richiederà
			la verifica di correttezza a livello di linting.
			Viene impostato anche l' ambiente focale, associato a questo progetto, che contiene
			il tool di verifica di linting
			
			Parameters
			----------
				project_name: str
					Una stringa contenente il nome del prossimo progetto focale a cui appartengono
					le test-suites parziali di cui si richiederà la verifica di correttezza
			
				full_root: str
					Una stringa contenente la Full Project Root Path del progetto focale a cui
					appartengono le test-suites parziali
					
				env_image: DockerImage
					Un oggetto `docker.models.images.Image` rappresentante l' immagine docker,
					pre-configurata, da utilizzare come ambiente per il progetto focale
					che si sta impostando
					
				path_prefix: str
					Una stringa contenente il path prefix utilizzato come Full Project Root Path
					all' interno dell' immagine docker fornita
				
			Raises
			------
				ValueError
					Si verifica se:
					
						- I parametri stringa hanno valore `None` o sono stringhe vuote
						- Il parametro `env_image` ha valore `None`
		"""
		if ((project_name is None) or (project_name == "") or
		    (full_root is None) or (full_root == "") or
			(path_prefix is None) or (path_prefix == "")
		):
			raise ValueError()
		
		# Stop dell' eventuale ambiente focale precedente
		if self._focal_env is not None:
			self._logger.log("Stop dell' ambiente focale ...") if self._logger is not None else None
			self._focal_env.stop_container()
			self._logger.log(f"Ambiente focale del progetto {self._proj_name} fermato") if self._logger is not None else None
			
			del self._focal_env
		
		self._proj_name = project_name
		self._full_root = full_root
		
		# Impostazione della path che conterrà il risultato delle verifiche di linting
		self._lint_result_path = f"{self._full_root}/gtsai__results/{self._RESULT_FNAME}"
		
		# Calcolo della path relativa dei risultati (con cui si costruirà quella assoluta
		# nell' ambiente focale)
		self._lint_result_relpath = path_relative(self._lint_result_path, start=self._full_root)
		
		self._focal_env = FocalContainer(
			env_image,
			self._full_root,
			path_prefix,
		)
		
		if not self._proj_set:
			self._proj_set = True
		
		# Avvio dell' ambiente focale (container)
		self._logger.log("Avvio dell' ambiente focale ...") if self._logger is not None else None
		self._focal_env.start_container()
		
		# Creazione della directory temporanea
		self._create_inputctr()

		self._logger.log(f"Ambiente focale del progetto {self._proj_name} avviato") if self._logger is not None else None


	def check_lintically(
			self,
			ptsuite_code: str
	) -> Dict[str, str]:
		"""
			Effettua il controllo di correttezza sintattica della test-suite parziale
			fornita come argomento
			
			Parameters
			----------
				ptsuite_code: str
					Una stringa contenente il codice della test-suite parziale di cui effettuare
					la verifica di correttezza sintattica
					
			Returns
			-------
				Dict[str, str]
					Un dizionario di stringhe, indicizzato da stringhe rappresentante il primo errore evidenziato
					dalla verifica di linting effettuata. Contiene opzionalmente:
						
						- "except_name": Il nome della problematica riscontrata nella verifica di linting effettuata
						- "except_mess": Il messaggio associato alla problematica riscontrata nella verifica di linting effettuata
						- "except_pos": Il numero di linea e colonna (separati da ";") in cui si trova la problematica riscontrata

					Se non si è verificato nessun errore viene restituito un dizionario vuoto
					
			Raises
			------
				ValueError
					Si verifica se il parametro `ptsuite_code` ha valore `None` o è una stringa vuota
					
				ProjectNotSetError
					Si verifica se:
						
						- Non è mai stato impostato un progetto focale
						- E' necessario re-impostare un progetto focale prima di eseguire di nuovo questa operazione
					
				OSError
					Se si verificano problemi con l' apertura, o scrittura, nel file temporaneo utilizzato
					per la verifica
		"""
		if (ptsuite_code is None) or (ptsuite_code == ""):
			raise ValueError()
		if not self._proj_set:
			raise ProjectNotSetError()
		if not self._inited:
			self._create_inputctr()
			
		self._logger.log(
			f"Inizio della verifica di linting ..."
		) if self._logger is not None else None
		
		self._logger.log("Scrittura della test-suite parziale nell' ambiente focale ...") if self._logger is not None else None
		tarfile_stream: BytesIO = BytesIO()
		ptsuite_code_b: bytes = ptsuite_code.encode("utf-8")
		with tarf_open(fileobj=tarfile_stream, mode="w") as tfptsuite:
			tarfile_info: TarInfo = TarInfo(name=path_split(self._ptsuite_relpath)[1])
			tarfile_info.size = len(ptsuite_code_b)
			tfptsuite.addfile(tarinfo=tarfile_info, fileobj=BytesIO(ptsuite_code_b))
		tarfile_stream.seek(0)
		self._focal_env.put_tararchive(
			f"{self._path_prefix}/{self._input_dir}",
			tarfile_stream
		)
		self._logger.log("Scrittura eseguita") if self._logger is not None else None
		
		# Richiesta della verifica della correttezza (a livello di linting)
		self._logger.log("Esecuzione della verifica di linting ...") if self._logger is not None else None
		self._focal_env.execute(
			f"/bin/bash -c 'python -m $LINTTOOLS_DIRNAME.{path_splitext(self._fenv_script_fname)[0]} "
			f"{self._ptsuite_relpath} {self._lint_result_relpath}'"
		)
		self._logger.log("Verifica di linting eseguita") if self._logger is not None else None
		
		# Lettura del risultato della verifica di correttezza
		self._logger.log("Lettura del risultato della verifica ...") if self._logger is not None else None
		json_dec: JSONDecoder = JSONDecoder()
		result: Dict[str, str] = None
		with open(self._lint_result_path, "r") as fjson:
			result = json_dec.decode(fjson.read())
		self._logger.log("Risultato della verifica letto") if self._logger is not None else None
		
		self._logger.log("Fine della verifica di linting") if self._logger is not None else None
		return result
	
	
	def clear_resources(self, stop_fenv: bool=False):
		"""
			Ripulisce le risorse che sono state utilizzate dal verificatore
			a livello di linting
			
			Parameters
			----------
				stop_fenv: bool
					Opzionale. Default = `False`. Un booleano che indica se arrestare l' istanza
					dell' ambiente focale che è stata avviata quando è stato impostato
					il progetto focale
		"""
		if stop_fenv and (self._focal_env is not None):
			self._logger.log("Stop dell' ambiente focale ...") if self._logger is not None else None
			self._focal_env.stop_container()
			self._logger.log(f"Ambiente focale del progetto {self._proj_name} fermato") if self._logger is not None else None
			self._proj_set = False
			
			del self._focal_env
			self._focal_env = None

		self._inited = False
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	def _create_inputctr(self):
		"""
			Crea la directory temporanea, internamente all' ambiente focale, per i files
			necessari all' esecuzione della verifica a livello di linting
		"""
		if not self._proj_set:
			raise ProjectNotSetError()
		
		try:
			self._focal_env.start_container()
			self._focal_env.stop_container()
			raise ContainerNotRunningError()
		except ContainerAlreadyRunningError:
			pass
		
		self._focal_env.execute(f"mkdir -p {self._path_prefix}/{self._input_dir}")
		
		self._inited = True