from typing import Tuple
# =========== ArgParse Utilities =========== #
from argparse import (
	ArgumentParser,
	Namespace as ArgumentsList,
)
# ========================================== #


def read_arguments(
		script_path: str
) -> ArgumentsList:
	"""
		Legge gli argomenti forniti alla chiamata di "exec_gents.py" da linea di comando
		
		Returns
		-------
			ArgumentList
				Un oggetto `argparse.Namespace` contenente come attributi:
					
					- `.config_root`: La root path che contiene i files di configurazione da utilizzare
					- `.platform`: Il nome della piattaforma di inferenza da utilizzare
					- `.config_type`: Il tipo dei files di configurazione utilizzato
					- `.platform_config`: Il nome (con estensione) del file di configurazione della piattaforma di inferenza
					- `.general_config`: Il nome (con estensione) del file di configurazione dei parametri generali di GenTestsAI
					- `.models_config`: Il nome (con estensione) del file di configurazione dei LLMs da utilizzare
					- `.projects_config`: Il nome (con estensione) del file di configurazione dei progetti focali
					- `.projsenv_config`: Il nome (con estensione) del file di configurazione dei parametri degli ambienti focali
					- `.prompts_config`: Il nome (con estensione) del file di configurazione dei prompts dei LLMs da utilizzare
	"""
	arg_parser: ArgumentParser = ArgumentParser(
		description="Main GenTestsAI's executable for generating test-suites",
		usage="python exec_gents.py [-p <inf_platform>] [-c <cfg_root_path>] [--config-type <file_type> [<config_names>]]"
	)
	
	arg_parser.add_argument(
		"-c", "--config-root",
		help='Optional. Root path that contains configuration files to use. '
		     'The default is the "config" directory inside GenTestsAI project\'s root' ,
		required=False,
		default=script_path
	)
	
	arg_parser.add_argument(
		"-p", "--platform",
		help='Optional. Inference platform to use to communicate with LLMs',
		required=False,
		default="ollama"
	)
	
	arg_parser.add_argument(
		"--config-type",
		help='Optional. File-type of the configuration files used',
		required=False,
		default="json"
	)
	config_names = arg_parser.add_argument_group(
		title="<config_names>",
		description=(
			"Configuration files name.\n"
			"Each argument is optional and independent.\n"
			"Any of these arguments requires that <configs_filetype> is specified"
			"\n"
			"--platform-config <platf_config_name>\n"
			"--general-config <general_config_name>\n"
			"--models-config <models_config_name>\n"
			"--projects-config <projs_config_name>\n"
			"--projsenv-config <projsenv_config_name>\n"
			"--prompts-config <platf_config_name>\n"
		)
	)
	
	arg_parser.add_argument(
		"--platform-config",
		help='Optional. Name of the file that contains platform configuration parameters',
		required=False,
		default="platform.json"
	)
	arg_parser.add_argument(
		"--general-config",
		help='Optional. Name of the file that contains general GenTestsAI configuration parameters',
		required=False,
		default="general.json"
	)
	arg_parser.add_argument(
		"--models-config",
		help='Optional. Name of the file that contains models configuration parameters',
		required=False,
		default="models.json"
	)
	arg_parser.add_argument(
		"--projects-config",
		help='Optional. Name of the file that contains focal projects configuration',
		required=False,
		default="projs.json"
	)
	arg_parser.add_argument(
		"--projsenv-config",
		help='Optional. Name of the file that contains focal environments configuration parameters',
		required=False,
		default="projs_environ.json"
	)
	arg_parser.add_argument(
		"--prompts-config",
		help='Optional. Name of the file that contains LLM prompts configuration',
		required=False,
		default="prompts.json"
	)
	
	args: ArgumentsList = arg_parser.parse_args()
	
	config_names_args: Tuple[str, ...] = (
        args.platform_config,
        args.general_config,
        args.models_config,
		args.projects_config,
		args.projsenv_config,
		args.prompts_config
	)
	if any(config_names_args) and not args.config_type:
		arg_parser.error("--config-type must be specified if any <config_names> is specified")
		
	return args