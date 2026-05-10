<div align="center">
	<img src="https://raw.githubusercontent.com/codesavant23/gentestsai/main/assets/logo/gtsai_github_socialcard.png" width="650"/>
</div>

[![Paper Backed](https://img.shields.io/badge/paper--backed-8A2BE2)](https://raw.githubusercontent.com/codesavant23/gentestsai/main/assets/thesis_ita.pdf)
![ReadMe](https://img.shields.io/badge/README.md-finished-%2320b706)
[![License](https://img.shields.io/badge/license-Custom--SA-%231b25e5)](https://raw.githubusercontent.com/codesavant23/gentestsai/main/assets/thesis_ita.pdf)
![Python](https://img.shields.io/badge/python-3.10%2B-35b2e3)
[![Docs](https://img.shields.io/badge/docs-uploaded--WIP-d37207)](https://codesavant23.github.io/gentestsai)

# What is GenTestsAI?

**GenTestsAI** is a sophisticated framework, rooted on the integrated SOLID-Designed library **GenTestsAILib**, for the automated generation of Python unit tests that uses Large Language Models (LLMs).<br/>

It orchestrates a complete pipeline that includes test generation, iterative syntactic and linting correction that is performed within isolated containerized environments called [**focal environments**](#framework-specific-terminology).
Optionally it provides also basic test coverage analysis (at statement level and [entity](#framework-specific-terminology)-level)

## Software artifacts Key Features

### GenTestsAI
*   **Comprehensive Configuration**: Offers deep customization through JSON configuration files for projects, models, prompts, LLM hyperparameters, and environment settings.
*   **LLM-Powered Test Generation and Correction**: Leverages the power of LLMs to automatically create unit tests for Python [autonomous entities](#framework-specific-terminology).
*   **Iterative Correction Loop**: Automatically subjects generated code to a rigorous two-phase correction process:
    1.  **Syntactic Correction**: Uses [`py_compile`](https://docs.python.org/3/library/py_compile.html) to check for syntax errors and subsequently prompts the selected LLM for fixes.
    2.  **Linting Correction**: Uses [`pylint`](https://www.pylint.org/) within a dedicated container environment ([focal environment](#framework-specific-terminology)) to identify and correct linting issues.
*   **Usage of focal environments**: Linting (static analysis) correctness check is performed in an isolated environment (that relies on containers) which grants security, scalability, portability and isolation of the host operating system.
*   **Intelligent Caching**: Relies on a [partial test suite](#framework-specific-terminology) caching system to store the results of generation and correction attempts, avoiding redundant API calls and speeding up subsequent runs that resumes an execution of the framework.
*   **Coverage Analysis**: Provides tools to calculate and evaluate the statement coverage of both human-written and AI-generated test suites using [`coverage.py`](https://github.com/coveragepy/coveragepy).
*   **Customizable Prompting**: Allows users to define their own prompt templates to guide the LLM's test generation and correction behavior for different models or tasks.

### GenTestsAILib
*   **Extreme Modularity & Extensibility**: Built with a SOLID-driven architecture, the library enables highly composable and interchangeable logical units across the entire GenTestsAI framework. Every layer — from inference platform backends and LLM specific implementations to configuration schemas, hyperparameters, and software groups installed in focal environments — is designed to be almost independently extendable, easily replaceable, and consistently maintainable, allowing seamless customization and evolution without heavily impacting existing components.
  A complete list of customizable/extendable layers of the architecture can be found in the official documentation (<font color="#22bc06">coming very soon, Lord permitting</font>. For now check the [associated paper](#associated-paper) (Italian language) in Chapter 10.3)
*   **Containerized Environments**: Builds and manages isolated Docker-compatible containers for each focal project, ensuring that dependency and environment conflicts are eliminated during linting checks.

# Project Structure

The repository is organized to separate the integrated library (GenTestsAILib), framework main executable scripts, which are functionally decomposed, tools used into each focal environment and configuration files.

| Path                    | Description                                                                                                    |
| ----------------------- | -------------------------------------------------------------------------------------------------------------- |
| `exec_*.py`             | Top-level executable scripts that serve as the main user-facing entry points for the framework's functionalities.   |
| `/logic`                | Contains the GenTestsAILib library, organized into macro-components, which provides LLM access, test generation, and more. |
| `/main_execs`           | Encapsulates the high-level framework orchestration logic (used by the `exec_*.py` scripts).                     |
| `/config`               | Holds all user-configurable files for projects, models, prompts, inference platform settings, etc.               |
| `/prompts`              | Contains template prompts in `.txt` files used to instruct the LLMs for generation and correction tasks.         |
| `/docker`               | Includes tools and resources, for linting and coverage calculation, that are deployed into the focal environments.  |
| `/caches`               | Default directory for storing partial test suite caches.                                                         |
| `/assets`               | Resources related to the software artifacts, used for this README.md file and documentation                    |

## Main Scripts

*   `exec_gents.py`: The primary script for the test generation and correction pipeline. It reads configurations, builds focal environments, and orchestrates the interaction between the code parser, selected LLMs and correctness checkers.
*   `exec_calc_coverage.py`: Executes the test coverage analysis pipeline. It runs the generated partial test suites, and human test suites, inside the appropriate project focal environment and generates coverage reports.
*   `exec_pdirs_hasher.py`: A command-line utility to generate an hash of a model name, used for creating standardized directory names for model-specific template prompts.
*   `exec_extract_projinfo.py`: A utility to scan project directories and extract utility metrics like Lines of Code (LOC) and the number of test cases.

# How It Works

The framework GenTestsAI operates through a series of orchestrated steps managed by its [main executable script `exec_gents.py`](#main-scripts):

1.  **Configuration Loading**: The system starts by reading configuration files, of the specified type and format, from the selected directory (default: `/config`). These files define the focal projects, the specific LLMs implementations to use, the inference platform details (e.g., Ollama API endpoint, if Ollama is chosen), template prompts to use for the tasks and general operational parameters.
2.  **Focal Environment Obtaining/Creation**: For each focal project selected, `exec_gents.py` builds, or obtains if already exists, a dedicated container image. This environment is configured with the project's specific Python version and dependencies (both Python and system-level) as defined in the configuration file for focal environments parameters (default: `projs_environ.json`), creating an isolated and consistent testing environment.
3.  **Code Extraction**: The script iterates through each selected Python module-file (`.py` file) of the current focal project, extracting focal functions and focal class methods for which generate test cases.
4.  **Test cases Generation & Correction**: For each extracted function or method:
    * A prompt is constructed using templates from the prompts directory (default: `prompts/`)  and sent to the current LLM that is generating/correcting tests.
    * GenTestsAI attempts to generate test cases for the current autonomous entity (function/method) and retrieve it from the LLM's response, creating the initial partial test suite.
    * This partial test suite enters a **syntactic correction loop**, where it's compiled. If an error occurs, the error message is fed back to the LLM in a new prompt to request a fix.
    * Once syntactically correct, the code enters a **linting correction loop**. It's checked using `pylint` inside the project's dedicated focal environment. If linting errors are found, they are sent back to the LLM for correction.
    * This process repeats until the code is both syntactically correct and passes linting, or until a maximum number of attempts, of each of the 2 processes, is reached.
    * In case of success the partial test suite is syntactically and lintically correct and it is written into a directory representing its module-file test suite.

Every generation and correction attempt's outcome is stored in caches of the technology specified (configured in the [caches settings file](#configuration-files)). 
This allows the system to quickly retrieve previously generated correct code without re-running the entire loop.

 Optionally, after generating the partial test suites `exec_calc_coverage.py` can be run to execute **coverage calculation**. The script obtains the same focal environments, or creates them from scratch, to execute test suites of each focal project, both human and AI-generated (for each LLM) against the focal code and measures statement coverage with `coverage.py`. GenTestsAI provides also the **possibility to aggregate the statement coverage**, resulting from coverage.py, **into autonomous entity coverage** (which measures the percentage covered of a focal autonomous entity).

Here you can find the [GenTestsAI Workflow Diagram](https://raw.githubusercontent.com/codesavant23/gentestsai/main/assets/generic_workflow_diagram_big_EN.png) which explains visually the steps described above (for a single focal project, and a single LLM)

# Configuration Files

GenTestsAI is highly configurable via "Dict-Like" configuration files located in a specific directory (default: `/config`) which type and format can vary.

Here's a list of the configuration files used by GenTestsAI, and a glimpse description of each one:
* **<u>Platform settings file</u>**: Specifies the LLM inference platform, the response timeout and the specific platform settings to use. For example, when using Ollama this includes the IP:Port of the device that hosts platform, authentication credentials, and connection timeouts.
* **<u>General settings file</u>**: Defines global settings, such as default hyperparameters for all models, maximum generation/correction attempts, and files/directories excluded from the generation process globally (for each focal project).
* **<u>Selected models settings file</u>**: Lists the specific LLMs implementations to generate and correct test cases. Here, you can override default hyperparameters for each model (e.g., `context_window`, `temperature`, `top-k`, etc.).
*   **<u>Selected focal projects file</u>**: Defines the focal Python projects for test generation, including their [Focal Root](#paths-and-directories) and [Tests Root](#paths-and-directories) paths. Optionally specific files or directories can be listed in order to exclude them from the generation.
*   **<u>Focal environments settings file</u>**: Defines parameters to configure focal environments for each project, including the base Docker image tag, paths to the environment tools, and scripts to run during the build process to pre-configure associated project dependencies.
*  **<u>Prompts settings file</u>**: Specifies prompt templates filenames for different tasks (functional, methodal, correctional), their base path,, and placeholder delimiters that composes templates.
*   **<u>Caches settings file</u>**: Defines the technology of caching system (e.g., `sqlite3`) and the location of the cache files to use/create.
*   **<u>Coverage calculation settings file</u>**: Configures parameters for the coverage calculation focal environment tool, such as the name of the `.coveragerc` file to be generated.

# Usage

Before running any scripts, ensure the configuration files, of the type and format selected, are in a selected config directory (here referred as `<cfg_root_path>`), and properly configured to match your projects, models, and local environment paths.

### **Generate Test Suites**:<br/>
Execute the main generation script. It will read your configuration and begin the process for all defined projects and models.
Parameter semantics and explanation can be found in the [documentation](https://codesavant23.github.io/gentestsai/)

   ```bash
    python exec_gents.py [-P <parser_tool>] [-p <inf_platform>]
		[-c <cfg_root_path>]
		[--config-type <file_type> [<config_names>]]
   ```

### **(Optional) Calculate Test Coverage**:<br/>
Optionally, after generation is complete, run the coverage script to analyze the generated tests.
Parameter semantics and explanation can be found in the [documentation](https://codesavant23.github.io/gentestsai/)

   ```bash
	python exec_calc_coverage.py [-p <inf_platform>]
		[-c <cfg_root_path>]
		[--config-type <file_type> [<config_names>]]
   ```

### **Setting specific model prompts**:<br/>
If you want to have specific prompts for one or more particular models, then you will need to hash the name of those models into digest of a desidered length. 
<font color="#e80808">**IMPORTANT: Make sure the number of characters use of the digest match the one set into the [General settings file](#configuration-files)**</font>

   ```bash
	python exec_pdirs_hasher.py [-a <hashing_algorithm>] [-c <num_chars>] <model_name>
   ```

# Appendix
## Associated Paper
Here you can find the [Bachelor's Thesis](https://raw.githubusercontent.com/codesavant23/gentestsai/main/assets/thesis_ita.pdf) (Italian language) in which GenTestsAI, and most of all GenTestsAILib, are presented formally.

## (Custom) Python Terminology
- **<u>Module-file</u>**: A Python module consisting of only a single file, with the extension `.py`, different from an `__init__.py` file.

- **<u>Code Package (or Module-package)</u>**: A Python module consisting of multiple files with the .py extension, generally identified by the name of the folder containing them, which must contain an `__init__.py` file that specifies the visibility of elements in the various "submodules" that comprise it (be they module-files or other module-packages).

- **<u>Python Module</u>**: A module-file or a module-package of Python code

## Framework specific Terminology

### General
- **<u>Focal Environment (of a focal project $X$):</u>**<br/> An isolated and pre-configured software environment aimed at hosting the focal project $X$, including the set of dependencies necessary for the execution, verification (static analysis/linting) and calculation of quality metrics of its source code, built according to one or more use cases among those listed.
<br/>

- **<u>Autonomous (Code) Entity:</u>**<br/> The smallest algorithmic unit of code whose semantics can be formalized in a contract (a function, or a class method).
<br/>

- **<u>Partial Test Suite of a Python module</u>**<br/> An organized and structured set of multiple test cases designed to verify the functionality, correctness, and reliability of a single autonomous code entity, of the focal Python module-file it concerns.
<br/>

- **<u>(Whole) Test Suite of a Python module</u>**<br/> An organized and structured set of multiple test cases, or partial test suites, designed to verify the functioning, correctness, and reliability of **each** autonomous code entity of the focal Python module it concerns.

### Paths and Directories
- **<u>Directory:</u>**  A folder in the o.s. file system.
- **<u>Path (of a directory $D$):</u>** An ordered sequence of directories that identifies the location of directory $D$ within the file system tree. A path can be expressed in absolute form (making the identification unique) or relative.
- **<u>Root Path (of an element $P$):</u>** A path identifying a directory $R$, ​​where $R$ represents the root directory containing all directories and files associated with element $P$.
<br/>

- **<u>Focal Project Root Path (also referred to as "Focal Root"):</u>** Root path of a focal project containing the source code (focal code) for which tests will be automatically generated. This directory may also include files or subdirectories not strictly related to the focal code.
- **<u>Tests Project Root Path (also referred to as "Tests Root"):</u>** Root path of a focal project containing test cases manually developed by human programmers.
- **<u>Gen-tests Project Root Path (also referred to as "Gen-tests Root"):</u>** Root path of a focal project intended to contain exclusively test cases automatically generated via Large Language Models.
- **<u>Env-config Project Root Path (also referred to as "Env-config Root"):</u>** Root path of a focal project containing the files required to configure its specific focal environment.
- **<u>Cov-config Project Root Path (also referred to as "Cov-config Root"):</u>** Root path of a focal project containing the files required to configure the tools for calculating coverage and other focal code quality metrics.
- **<u>Full Project Root Path (also referred to as "Full Root"):</u>** Root path of a focal project that includes the entire contents of the project involved in an automatic test case generation process and a test evaluation process. Specifically, it contains:
	- as subdirectories at the **first level**:
		- the Gen-tests Project Root Path
		- the Env-config Project Root Path 
		- the Cov-config Project Root Path 
	- as subdirectories at **arbitrary nesting** levels:
		- the Focal Project Root Path
		- the Tests Project Root Path
