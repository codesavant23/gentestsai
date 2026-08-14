<div align="center">
	<img src="/gentestsai/assets/gtsai_logoart.png" />
</div>
<br/>

**GenTestsAI** is a Python framework that automatically generates test cases, of a provided Python codebase, leveraging LLM-based workflows.

This framework has been developed using the library **[GenTestsAILib](gtsai_lib/intro/) as its foundational layer** which implements basic generation workflows composed by the framework GenTestsAI.

## Generative implemented workflow

The generative workflow implemented by GenTestsAI aims to be simple but complete in performed processes.

In particular GenTestsAI, in addition to the expected generation of test cases, ensures also their the syntactical correction and correction based on static analysis (linting).

The diagram below visually represents the entire generative workflow implemented by GenTestsAI

<div>
	<img src="/gentestsai/assets/generative_workflow.png" />
	<p class="figure-descr">Figure: Complete generative workflow of GenTestsAI</p>
</div>

The generative workflow is decomposed in the following processes and steps:

- Loading framework's **configuration**
- For each Python module (module-file) in a given project codebase
	1. **Extracts code** from focal function/methods (called [autonomous entities](/gentestsai/common/glossary/#entity)) 
	2. For each autonomous entity
		1. Requests the **<font color="#2F9E44">generation of its test cases</font> to** the selected **LLM** up to a max of the established number of generation tries
			1. If the generation is successful a [partial test suite](/gentestsai/common/glossary/#ptsuite) has been obtained
			2. If there are <u>no more tries</u> the **autonomous entity is declared skipped** and the framework advances by 1 autonomous entity
		2. **Checks** the <font color="#CE2ED7">**syntactical correctness**</font> of the generated partial test suite
			1. If it's <u>not correct</u> **requests a syntactical correction** to the selected LLM
			2. If there are <u>no more tries</u> the **<font color="#2F9E44">partial test suite</font> is discarded** and the **autonomous entity is declared skipped** and the framework advances by 1 autonomous entity
			3. If not retries the check (_Returns to step <font color="#888FA4">ii.</font>_)
		3. Performs <font color="#F08C00">**static analysis**</font>, checking the **linting-level correctness** of the syntactical correct partial test suite
			1. If it's <u>not correct</u> **requests a lintical correction** to the selected LLM
			2. If there are <u>no more tries</u> the **<font color="#CE2ED7">partial test suite</font> is discarded** and the **autonomous entity is declared skipped** and the framework advances by 1 autonomous entity
			3. If not retries the check (_Returns to step <font color="#888FA4">iii.</font>_)
		4. If all the steps **complete <u>with success</u>** the partial test suite is considered executable and it's **written to file** into the **folder representing the current focal module test suite**
		5. Then the framework advances by 1 autonomous entity