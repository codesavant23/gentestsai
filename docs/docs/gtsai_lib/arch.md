GenTestsAILib is structured as a set of high-level components, each responsible for one or more well-defined interrelated concerns, within the hypotized automated test generation domains.

The architecture reflects a deliberate separation of responsibilities, where each macro-component encapsulates a specific aspect of the system while interacting with others through clear interfaces (implemented by code interfaces and stable classes). 
This library follows SOLID design principles eventhough the Python language itself doesn't promote them.

Anyway, the combination of this organization and principles enables independent evolution of components, and supports the construction of flexible test generation workflows.

An architectural diagram of GenTestsAILib is provided below.

<div>
	<img src="/gentestsai/assets/archs/arch_diagram.png" />
	<p class="figure-descr">Figure: Architectural components diagram of GenTestsAILib (v1.1.2)</p>
</div>


## Historical note

Initially GenTestsAILib was developed for the GenTestsAI project and, eventhough was designed as a decoupled and resusable library, was built internally to the GenTestsAI project containing also fully detachable components.

Today those components has been fully separated from GenTestsAILib becaming independant Python components, freely to evolve by themselves

If you're interested you can take a look at the [historical architecture](../hist_arch) of the library. 


## Components explanation

Here's an explanation of the services provided by each component of the library.

The order of explanation followed is from **the most central to the most peripheral** one.

### `ptsuite_generation` component

This component provides core services that fulfill main library use cases. In particular it provides:

- **Syntactic and linting** (static analysis) [partial test suite](../../common/glossary#ptsuite) checking _(by interface [`ISyntacticChecker`](../../hiers/gtsai_lib/interfaces/ISyntacticChecker) and stable class [`LintingChecker`](../../hiers/gtsai_lib/classes/LintingChecker))_
- Partial test suite **generation** _(by stable class [`EntityPtsuiteGenerator`](../../hiers/gtsai_lib/classes/EntityPtsuiteGenerator))_
- **Syntactic and linting** partial test suite **correction** _(by stable classes [`PtsuiteSyntacticCorrector`](../../hiers/gtsai_lib/classes/PtsuiteSyntacticCorrector) and [`PtsuiteLintingCorrector`](../../hiers/gtsai_lib/classes/PtsuiteLintingCorrector))_

### `focalproj_configuration` component

This component provides all the services related to the configuration of a focal project.
In particular it provides the services needed for handling [focal environments](../../common/focal_envs).

These services are:

- Possibility to **create incrementally** a **[container build description](../../common/glossary#cbd) file** _(through interface [`IDockfBuilder`](../../hiers/gtsai_lib/interfaces/IDockfBuilder))_
- Build/create focal environment images _(through interface [`IFocalEnvConfigurator`](../../hiers/gtsai_lib/interfaces/IFocalEnvConfigurator))_ and consequently clean building cache _(through interface [`IBuildCacheCleaner`](../../hiers/gtsai_lib/interfaces/IBuildCacheCleaner))_ 
- Handle running focal environments instances _(using stable class [`FocalContainer`](../../hiers/gtsai_lib/classes/FocalContainer))_