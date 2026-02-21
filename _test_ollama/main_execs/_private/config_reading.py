from typing import List, Tuple, Dict, Any

# ============ Path Utilities ============ #
from os.path import (
	join as path_join,
	split as path_split,
)
# ======================================== #

from logic.variability import EImplementedPlatform
from logic.configuration.config_parser import IConfigParser
from logic.configuration.config_validator import (
	IConfigValidator,
	AccessorPlatSpecCfgValidatorFactory, GeneralPlatSpecCfgValidatorFactory, ModelsPlatSpecCfgValidatorFactory,
	AAccessorConfigValidator, AGeneralConfigValidator, AModelsConfigValidator,
	ProjectsConfigValidator, ProjsEnvironConfigValidator,
	PromptsConfigValidator, CacheConfigValidator
)



def read_platform_config(
		config_root: str,
		config_fname: str,
		config_parser: IConfigParser,
		cfgval_f: AccessorPlatSpecCfgValidatorFactory,
		inf_platf: EImplementedPlatform,
) -> Dict[str, Any]:
	# Lettura del file della piattaforma di inferenza
	platf_dict: Dict[str, Any] = config_parser.read_config(path_join(config_root, config_fname))
	platf_chker: AAccessorConfigValidator = cfgval_f.create(inf_platf, platf_dict)
	platf_chker.validate_sem()
	return platf_dict


def read_general_config(
		config_root: str,
		config_fname: str,
		config_parser: IConfigParser,
		cfgval_f: GeneralPlatSpecCfgValidatorFactory,
		inf_platf: EImplementedPlatform,
) -> Dict[str, Any]:
	# Lettura del file dei parametri generali
	gen_dict: Dict[str, Any] = config_parser.read_config(
		path_join(config_root, config_fname)
	)
	gen_chker: AGeneralConfigValidator = cfgval_f.create(inf_platf, gen_dict)
	gen_chker.validate_sem()
	return gen_dict


def read_models_config(
		config_root: str,
		config_fname: str,
		config_parser: IConfigParser,
		cfgval_f: ModelsPlatSpecCfgValidatorFactory,
		inf_platf: EImplementedPlatform,
) -> Dict[str, Any]:
	# Lettura del file dei modelli
	models_dict: Dict[str, Any] = config_parser.read_config(
		path_join(config_root, config_fname)
	)
	llms_chker: AModelsConfigValidator = cfgval_f.create(inf_platf, models_dict)
	llms_chker.validate_sem()
	return models_dict


def read_projs_config(
		config_root: str,
		config_fname: str,
		config_parser: IConfigParser,
) -> Dict[str, Any]:
	# Lettura del file dei progetti focali
	projs_dict: Dict[str, Any] = config_parser.read_config(
		path_join(config_root, config_fname)
	)
	projs_chker: IConfigValidator = ProjectsConfigValidator(projs_dict)
	projs_chker.validate_sem()
	return projs_dict


def read_projsenv_config(
		config_root: str,
		config_fname: str,
		config_parser: IConfigParser,
		projs_dict: Dict[str, Any],
		docker_hub_vers: str
) -> Dict[str, Any]:
	# Lettura del file dei parametri degli ambienti focali
	full_roots: List[str] = list()
	for _, proj_info in projs_dict.items():
		full_roots.append(
			 path_split(proj_info["focal_root"])[0]
		)
	environ_dict: Dict[str, Any] = config_parser.read_config(
		path_join(config_root, config_fname)
	)
	environ_chker: IConfigValidator = ProjsEnvironConfigValidator(
		environ_dict, full_roots, docker_hub_vers
	)
	environ_chker.validate_sem()
	return environ_dict


def read_prompts_config(
		config_root: str,
		config_fname: str,
		config_parser: IConfigParser
) -> Dict[str, Any]:
	# Lettura del file dei prompts da utilizzare
	prompts_dict: Dict[str, Any] = config_parser.read_config(
		path_join(config_root, config_fname)
	)
	prompts_chker: IConfigValidator = PromptsConfigValidator(prompts_dict)
	prompts_chker.validate_sem()
	return prompts_dict


def read_caches_config(
		config_root: str,
		config_fname: str,
		config_parser: IConfigParser
) -> Dict[str, Any]:
	# Lettura delle caches di test-suites parziali da utilizzare
	caches_dict: Dict[str, Any] = config_parser.read_config(
		path_join(config_root, config_fname)
	)
	caches_chker: IConfigValidator = CacheConfigValidator(caches_dict)
	caches_chker.validate_sem()
	return caches_dict


def read_config_files(
		config_root: str,
		config_parser: IConfigParser,
		inf_platf: EImplementedPlatform,
		file_names: Tuple[str, ...],
		docker_hub_vers: str = "v2"
) -> Dict[str, Dict[str, Any]]:
	"""
		Legge i files di configurazione di GenTestsAI
		
		Parameters
		----------
			config_root: str
				Una stringa rappresentante la root path che contiene i files di configurazione
				da utilizzare
				
			config_parser: IConfigParser
				Un oggetto `IConfigParser` rappresentante il parser di files di configurazione
				da utilizzare per la lettura
				
			inf_platf: EImplementedPlatform
				Un valore `EImplementedPlatform` rappresentante la piattaforma di inferenza scelta
		
			file_names: Tuple[str, ...]
				Una tupla di 7 stringhe contenente i nomi dei files di configurazione da utilizzare:
					
					- [0]: Il nome del file di configurazione della piattaforma di inferenza
					- [1]: Il nome del file di configurazione dei parametri generali
					- [2]: Il nome del file di configurazione dei LLMs utilizzati
					- [3]: Il nome del file di configurazione dei progetti focali utilizzati
					- [4]: Il nome del file di configurazione dei parametri per gli ambienti focali
					- [5]: Il nome del file di configurazione dei prompts da utilizzare
					- [6]: Il nome del file di configurazione delle caches di test-suites parziali da utilizzare
					
			docker_hub_vers: str
				Opzionale. Default = `v2`. Una stringa rappresentante la versione del "Docker Hub" da utilizzare
				(viene utilizzata dal validatore della configurazione degli ambienti focali)
		
		Returns
		-------
			Dict[str, Dict[str, Any]]
				Un dizionario, di dizionari variegati stringa-indicizzati, indicizzato a sua volta da stringhe
				contenente i files di configurazione letti in dizionari Python. In particolare contiene:
				
					- "platform": Il file di configurazione della piattaforma di inferenza (vedi `AAccessorConfigValidator` per i suoi campi)
					- "general": Il file di configurazione dei parametri generali (vedi `AGeneralConfigValidator` per i suoi campi)
					- "models": Il file di configurazione dei LLMs utilizzati (vedi `AModelsConfigValidator` per i suoi campi)
					- "projects": Il file di configurazione dei progetti focali utilizzati (vedi `ProjsConfigValidator` per i suoi campi)
					- "environ": Il file di configurazione dei parametri per gli ambienti focali (vedi `ProjsEnvironConfigValidator` per i suoi campi)
					- "prompts": Il file di configurazione dei prompts da utilizzare (vedi `PromptsConfigValidator` per i suoi campi)
					- "caches": Il file di configurazione delle caches di test-suites parziali da utilizzare (vedi `CacheConfigValidator` per i suoi campi)
	"""
	configs: Dict[str, Dict[str, Any]] = dict()
	
	platf_cfgvalf: AccessorPlatSpecCfgValidatorFactory = AccessorPlatSpecCfgValidatorFactory()
	general_cfgvalf: GeneralPlatSpecCfgValidatorFactory = GeneralPlatSpecCfgValidatorFactory()
	models_cfgvalf: ModelsPlatSpecCfgValidatorFactory = ModelsPlatSpecCfgValidatorFactory()

	configs["platform"] = read_platform_config(config_root, file_names[0], config_parser, platf_cfgvalf, inf_platf)
	configs["general"] = read_general_config(config_root, file_names[1], config_parser, general_cfgvalf, inf_platf)
	configs["models"] = read_models_config(config_root, file_names[2], config_parser, models_cfgvalf, inf_platf)
	configs["projects"] = read_projs_config(config_root, file_names[3], config_parser)
	configs["environ"] = read_projsenv_config(config_root, file_names[4], config_parser, configs["projects"], docker_hub_vers)
	configs["prompts"] = read_prompts_config(config_root, file_names[5], config_parser)
	configs["caches"] = read_caches_config(config_root, file_names[6], config_parser)
	
	return configs