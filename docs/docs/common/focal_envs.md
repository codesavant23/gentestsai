One of the core concepts introduced by **GenTestsAILib** (and subsequently GenTestsAI) is the **Focal Environment**.

A Focal Environment is an isolated, pre-configured software environment dedicated **to a single [focal project](../glossary#focal-project)**.
Its purpose is to provide a specific project environment of deterministic and reproducible execution for all operations that require interacting with the project, such as static analysis and coverage computation.

In GenTestsAILib, Focal Environments are implemented as **Docker-compatible containers**.
Any container engine compatible with the Docker image format (such as Docker or Podman) can therefore be used.

## Why Focal Environments?

Many operations performed during automatic test generation depend on the availability of a correctly configured execution environment.

For example:

* static analysis requires the project's dependencies and the analysis tools to be available;
* coverage computation requires the project to be executed in a controlled environment;
* different projects may require different Python versions and/or different dependency sets.

Instead of relying on the host machine, GenTestsAILib executes these operations inside a dedicated container.
This guarantees that analyses are not only reproducible, but completely independent from the host system.

This isolation is particularly important for the **semantic correction** phase provided by GenTestsAILib, where generated tests are validated through static analysis before being accepted.


## Focal Environment Images

Every Focal Environment is created from a dedicated container image. The image is built specifically for a given focal project while following a common structure understood by GenTestsAILib.

### Pre-installed Software

Every Focal Environment always includes the following software:

- a specific version of **Python**
- **Pylint**, used for static analysis
- **coverage.py**, used for coverage computation

Additional software can be installed according to the environment configuration files used to build the image.

### Directory Layout

Internally, every Focal Environment follows the directory structure shown below.

```text
<path prefix>/
├── project/ 🗂️
│	⋮
│   └── <cov-config root>/
├── tools/ 🛠️
│   ├── <linttools root>/
│	│	⋮
│   │   └── <lintcheck script>.py ☑️
│   └── <covtools root>/
│		⋮
│       └── <covcalc script>.py ✅
└── <env-config root>/ ⚙️
```

#### `<path prefix>/`

This directory is the **root directory of the Focal Environment contents**. It contains every file and directory managed by GenTestsAILib inside the container, excluding the operating system itself.

Its name is user-defined.

#### 🗂️ `project/`

This directory contains everything related to the focal project. It corresponds to the project's [**full root**](../glossary#full-root) inside the Focal Environment.

##### `<cov-config root>/`

Contains the configuration files used for coverage computation.

Its name is user-defined.

#### 🛠️ `tools/`

Contains all the auxiliary tools used by the Focal Environment.

##### `<linttools root>/`

Contains the scripts and utilities used to perform static analysis (linting).
Its name is user-defined.

The static analysis is run/performed by a Python script, contained in the directory, whose name is user-defined (identified by ☑️ in the [tree structure](#directory-layout) above).

##### `<covtools root>/`

Contains the scripts and utilities responsible for computing coverage.
Its name is user-defined.

The coverage computation is run/performed by a Python script, contained in the directory, whose name is user-defined (identified by ✅ in the [tree structure](#directory-layout) above).

#### ⚙️ `<env-config root>/`

Contains the configuration files that were used to build the Focal Environment itself.

Its name is user-defined.

### Environment Variables

Every Focal Environment always defines the following environment variables.

| <div style="width:6.5rem">Variable</div> | Description                                                                                                                    |
|------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| `PYTHON_VERSION`                         | Version of Python installed inside the environment.                                                                            |
| `PYTHONPATH`                             | Python search path. It always includes `<path prefix>/` and `<path prefix>/project/`, in addition to any other required paths. |
| `FULL_ROOT`                              | Path to `<path prefix>/project/`.                                                                                              |
| `FOCAL_ROOT`                             | Path to the directory containing the project's source code, located inside `project/`.                                         |
| `GENTESTS_ROOT`                          | Path to the directory containing the generated tests, located inside `project/`.                                               |
| `CONTTOOLS_ROOT`                         | Path to `<path prefix>/tools/`.                                                                                                |
| `LINTTOOLS_DIRNAME`                      | Name of the directory containing the static analysis tools inside `tools/`.                                                    |
| `COVTOOLS_DIRNAME`                       | Name of the directory containing the coverage tools inside `tools/`.                                                           |


## Focal Environment Instances

A Focal Environment image is only a template.

Whenever GenTestsAILib needs to execute analyses, it creates, or uses, a **Focal Environment instance** from the corresponding image.

The library provides the `FocalContainer` class to create, manage and destroy these container instances.

Each instance is configured specifically for its focal project while preserving the standardized structure described above.

### Shared Directories

When a Focal Environment is instantiated through `FocalContainer`, GenTestsAILib also creates a **results directory** shared between the container and the host machine.

This directory acts as the communication channel between the isolated environment and the application (or framework) built on top of GenTestsAILib.

The static analysis tools and the coverage computation scripts store their outputs in this directory, allowing the host application to retrieve and process the produced data.

Inside the container, the results directory is created as a direct child of `<path prefix>/`, alongside `project/` and `tools/`.
Its name is user-defined.