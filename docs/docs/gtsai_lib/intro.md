<div align="center">
	<img src="/assets/gtsai_lib_logoart.png" />
</div>
<br/>

# Introduction
**GenTestsAILib** is a Python software library designed to support automated test case generation for Python code within LLM-based workflows.

Originally developed as the foundational layer of the GenTestsAI framework, it provides a set of modular and decoupled components that enable the construction of 
flexible and maintainable test generation processes. While tightly integrated into GenTestsAI, the library is intentionally designed to be *fully*, or *partially*, reusable beyond its original context.

## Architecture
The design of GenTestsAILib is based on [**SOLID principles**](https://en.wikipedia.org/wiki/SOLID), which guided the decomposition of the test generation processes into well-defined conceptual elements. 
In contrast to common practices in dynamic languages such as Python — where such principles are often overlooked, and even underestimated or blamed — GenTestsAILib adopts a structured architectural approach to **ensure long-term code quality and robustness**.

Each component is responsible for a specific concern, exposing clear **interfaces** and relying on **stable concrete classes**. Here **contracts** for the use of code elements (classes and methods) play a **fundamental role**. This approach promotes high cohesion and low coupling, resulting in a system that is easier to extend, maintain, and evolve over time. 

### Library Components
The library is organized into a set of modular components, each addressing a distinct aspect of the overall system. These include modules such as `configuration`, `ptsuite_generation`, `focalproj_configuration`, `decls_extraction`, `calc_coverage`, and `utils`. Each module encapsulates a specific macro-responsibility within the broader test generation domain, **contributing to a composable** and **extensible architecture**.

A high-level overview of these components and their weak relationships is provided in the architectural diagram below.

<div>
	<img src="/assets/arch_diagram.png" />
	<p class="figure-descr">Figure: Architectural components diagram of GenTestsAILib</p>
</div>

## Target audience

GenTestsAILib is intended for developers, testers, and researchers interested in building or experimenting with automated test generation systems. Although it originated in an academic context and continues to evolve, it is built upon a grounded architectural foundation that supports iterative refinement and extension. Its design enables both its use as the core of the GenTestsAI framework and its adoption as a general-purpose library in other contexts where modular, maintainable test generation solutions are required.