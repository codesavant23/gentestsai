# Architectural Overview

GenTestsAILib is structured as a set of high-level components, each responsible for one or more well-defined interrelated concerns, within the hypotized automated test generation domains. The architecture reflects a deliberate separation of responsibilities, where each macro-component encapsulates a specific aspect of the system while interacting with others through clear interfaces and/or stable classes. This organization enables independent evolution of components and supports the construction of flexible test generation workflows.


## Configuration

The `configuration` component is responsible for managing the configuration of systems built using GenTestsAILib. It provides mechanisms for parsing and handling configuration files while decoupling the parsing logic from the semantic purpose of each configuration.

This separation allows different configuration dimensions --- such as general parameters, model-specific settings, or other domain-specific configurations --- to evolve independently. As a result, the system can be extended by introducing new configuration types or formats without affecting existing ones.


## Partial Test Suite Generation

The `ptsuite_generation` component represents the core of the library. It is responsible for the generation, validation, and refinement of partial test suites, forming the backbone of the automated test generation processes assembled with GenTestsAILib.

It is internally organized into three main sub-components:

- `generation`: implements the logic for generating partial test suites leveraging LLMs.
- `checking`: provides syntactic and semantic validation mechanisms, in particular linting-based verification.
- `correction`: implements correction software services to fix issues identified during the checking phase, both at syntactic and semantic (linting) levels.

Together, these sub-components enable the construction of iterative processes in which generated test cases are validated and refined to improve their correctness and quality.

A detailed component diagram is provided below.

<div>
	<img src="/assets/ptsuite_generation_diagram.png" />
	<p class="figure-descr">Figure: "ptsuite_generation" component diagram</p>
</div>


## Focal Environments Configuration

The `focalproj_configuration` component is responsible for the construction and management of focal environments, which are required to execute and validate generated partial test suites against the target code.

It is composed of the following sub-components:

- `dockerfile_builder`: provides services for the incremental construction of *Container Build Description* files.
- `focal_env.focalenv_configurator`: provides configurators responsible for building focal environments, with respect to selected characteristics.
- `focal_container`: manages the lifecycle and execution of focal environments.

This component abstracts the complexity of focal environments setup and execution, enabling reproducible and isolated test evaluation.

A detailed component diagram is provided below.

<div>
	<img src="/assets/focalproj_cfgor_diagram.png" />
	<p class="figure-descr">Figure: "focalproj_configuration" component diagram</p>
</div>


## Focal Declarations Extraction

The `decls_extraction` component provides services for extracting structural elements from the focal codebase. These elements are used as inputs for the test generation process built upon GenTestsAILib.


## Coverage Calculation

The `calc_coverage` component provides services for measuring code coverage achieved by generated test suites. It supports both statement-level coverage and entity-level coverage, enabling quantitative evaluation of test cases effectiveness.


## Utilities

The `utils` component provides cross-cutting services used throughout the library. These include functionalities such as prompt building for LLM interactions, logging utilities, and other shared mechanisms that support overall systems developed with the library.