## Software testing terminology

- <span id="focal-project">**Focal project**: Target project, also known as [Software/System Under Testing (SUT)](https://en.wikipedia.org/wiki/System_under_test)</span>


## Python language (custom) terminology

- <span id="module-file">**Module-file**: Python module consisting of only a <u>single file</u>, with the extension .py, different from an `__init__.py` file</span>
- <span id="package">**Code Package** (or Module-package): Python module consisting of <u>multiple module-files</u>, generally identified by the name of the folder containing them, which must contain an `__init__.py` file that specifies the visibility of the contained elements</span>
- <span id="module">**Python Module**: Module-file or a code package</span>
- <span id="code-element">**Code Element**: Interface/abstract class/enumerator/class, generic term for all of them</span>


## Projects specific terminology/concepts

### General

- <span id="focal-env">**Focal Environment (of a focal project $X$)**:
	Isolated and pre-configured software environment aimed at hosting the focal project $X$, including the set of dependencies necessary for the execution, verification (static analysis) and calculation of quality metrics of its source code, built according to one or more use cases (among those just listed)</span>
- <span id="entity">**Autonomous (Code) Entity**: Smallest algorithmic unit of code whose semantics can be formalized in a contract (a function, or a class method)</span>
- <span id="ptsuite">**Partial Test Suite of a Python module**: Organized and structured set of multiple test cases designed to verify the functionality, correctness, and reliability of a single autonomous code entity, of the focal Python module-file it concerns</span>
- <span id="tsuite">**(Whole) Test Suite of a Python module**: Organized and structured set of multiple test cases, or partial test suites, designed to verify the functioning, correctness, and reliability of each autonomous code entity of the focal Python module it concerns</span>

### Paths and directories in general

- <span id="directory">**Directory**: Folder in the o.s. file system.</span>
- <span id="path">**Path (of a directory $D$ )**: Ordered sequence of directories that identifies the location of directory $D$ within the file system tree. A path can be expressed in absolute form (making the identification unique) or relative.</span>
- <span id="root-path">**Root Path (of an element $P$ )**: Path identifying a directory $R$, where $R$ represents the root directory containing all directories and files associated with element $P$.</span>

### Projects specific directory concepts

- <span id="func-decomp-dir">**Functional decomposition package**: Code package used to decompose functionally the code of executables building the GenTestsAI framework</span>

### Projects specific root paths concepts

- <span id="focal-root">**Focal Project Root Path** (also referred to as "Focal Root"): Root path of a focal project containing the source code (focal code) for which tests will be automatically generated. This directory may also include files or subdirectories not strictly related to the focal code.
- <span id="tests-root">**Tests Project Root Path** (also referred to as "Tests Root") Root path of a focal project containing test cases manually developed by human programmers.
- <span id="gentests-root">**Gen-tests Project Root Path** (also referred to as "Gen-tests Root"): Root path of a focal project intended to contain exclusively test cases automatically generated via Large Language Models.
- <span id="envconfig-root">**Env-config Project Root Path** (also referred to as "Env-config Root"): Root path of a focal project containing the files required to configure its specific focal environment.
- <span id="covconfig-root">**Cov-config Project Root Path** (also referred to as "Cov-config Root"): Root path of a focal project containing the files required to configure the tools for calculating coverage and other focal code quality metrics.
- <span id="full-root">**Full Project Root Path** (also referred to as "Full Root"): Root path of a focal project that includes the entire contents of the project involved in an automatic test case generation process and a test evaluation process. Specifically, it contains:</span>
	- as subdirectories at the first level:
		- the Gen-tests Project Root Path
        - the Env-config Project Root Path
        - the Cov-config Project Root Path
    - as subdirectories at arbitrary nesting levels:
        - the Focal Project Root Path
        - the Tests Project Root Path