Both GenTestsAILib and GenTestsAI uses **project specific conventions** which are fundamental to understand both project structures.

These conventions are adopted to improve code organization, readability, and maintainability.

In particular, they are used to:

- Simulate access modifiers (for classes, enums, methods, and other code members) **that are not present in Python** but necessary in any advanced OO programming language to ensure complex semantic behaviour;
- Enforce a consistent structural order of both codebases;
- Clearly distinguish the public API from internal implementation details. 

These conventions also helps restrict the visibility of [code elements](../glossary#code-element) within software components or packages, **promoting encapsulation** and reducing unintended dependencies to internal implementation details.

## Files conventions

- Every [module-file](../glossary#module-file) contains **exactly 1 abstraction/class/enumerator**

### Access specifiers

- A file that **starts with `_`** is considered to be **<u>public within its package</u>** but **<u>private outside</u>** of it (similiar to Java's `package` access specifier)
- <span id="file-visib">Any file that is **<u>not</u> explicitly exposed** by its package is **considered to be private outside**</span>

### Relating to content description

- A file that **start with `i_`** indicates that an **<font color="#cd13ca">interface definition</font>** resides in that file
- A file that **start with `a_`** indicates that an **<font color="#1358d7">abstract class definition</font>** resides in that file
- A file that **start with `e_`** indicates that an **<font color="#30ae1a">enumerator definition</font>** resides in that file
- Every other module-file, that is **<u>not</u> in a [functional decomposition](../glossary#func-decomp-dir) package** contains a **<font color="#c7bd05">class definition</font>**

## Packages and sub-packages conventions

### Access specifiers

- Every package that **start with `_`** is considered to be **<u>public within its parent-package</u>** but **<u>private outside its parent-package</u>** (similiar to Java's `package` access specifier).<br/>These types of packages will be called <font color="#6d6d6d">_**private packages**_</font>
- Everything contained in a <font color="#6d6d6d">_private package_</font> is considered to be **only visible within that same package, and in its sub-packages**
- Only code elements **<u>explicitly exposed</u>** by the package containing them are **considered to be public outside** their package (correlated to [_file visibility rule_](#file-visib))

### Relating to Structure

- Every public package containing a **class hierarchy** will be called <font color="#d75900">_**hierarchy package**_</font>
- Each <font color="#d75900">_hierarchy package_</font> **contains a `_private` folder** which hides hierarchy implementation files 
- Each <font color="#d75900">_hierarchy package_</font> **<u>can</su> contain a `exceptions` sub-package** which exposes hierarchy-specific exceptions
- Each <font color="#d75900">_hierarchy package_</font> **<u>can</u> contain a `_factory` folder** if the hierarchy provides a factory (or hierarchy of factories) that instatiates its objects. The `_factory` folder is used to hide factory implementation files
- The [code elements](../glossary#code-element) of both `_private` and `_factory` folders that should be public are **<u>explicitly exposed</u> by the package containing those folders**

### Specific projects packages type

- The [functional decomposition package](../glossary#func-decomp-dir) is called `logic`

## Abstractions, classes and enumerators conventions

### Access specifiers

- Every [code element](../glossary#code-element) whose name **starts with a `_`** is considered to be **<u>public within its parent-package</u>**, **and** by its **<u>extenders</u>**.

### Relating to content description

#### Relating to the type of code element

- Every code element whose name **starts with an `I` and** is followed by a **capital letter** is an **<font color="#cd13ca">interface definition</font>**
- Every code element whose name **starts with, or has as 2nd character, an `A` and** is followed by a **capital letter** is an **<font color="#1358d7">abstract class definition</font>**
- Every code element whose name **starts with an `E` and** is followed by a **capital letter** is an **<font color="#30ae1a">enumerator definition</font>**
- Every code element whose name **does not match anyone of the rules above** is a **<font color="#c7bd05">class definition</font>**

#### Relating to specific semantic meaning

- Every [code element](../glossary#code-element) that **ends with `Error`** represents an **exception**
- Every code element that **ends with `Factory`** represents a **factory** of objects
- Every code element that **ends with `FactoryResolver`** represents a **factory of factories** (used to completely abstract an implementation of an [Abstract Factory Pattern](https://en.wikipedia.org/wiki/Abstract_factory_pattern))