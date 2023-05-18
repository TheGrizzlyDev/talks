---
marp: true
title: Bazel: What's Bazel? Why should you care?
author: Antonio Di Stefano
date: 23/05/2023
---

# What's Bazel? Why should you care?

---

## What is this talk about?

- What is a build system?
- A short history of build systems
- Challenges faced by builds at a large scale
- Introduction to Bazel

---

## Who am I?

Antonio Di Stefano

DevEx engineer @ Engflow

---

## What is a build system?

A build system is a tool that helps you go from source code to deployable artifacts. It includes tasks such as:
- Compiling code
- Generating code
- Running tests
- Packaging artifacts (e.g., Docker images, JARs, .deb, .tar.gz, etc.)

---

## Challenges of Build Systems

- Speed and Efficiency
- Reproducibility
- Configurability
- Extensibility
- Integrations

---

# History of Build Systems

---

# DIY builds with shell scripting

```bash
g++ -Wall ... -o lib lib.cc
g++ -Wall ... -o main main.cc
g++ -Wall ... -o test test.cc
./test
```

---

### Pros:

- Maintaining this build will guarantuee job stability for a while
- Can technically be used with any lanuage/platform

### Cons:

- Not very portable
- Requires setup for each workstation
- No caching from the build
- Hard to parallelize and speed-up
- Bespoke configuration
- No integration with tools
- Cannot trivially target a subset of the build

---

## Make

```make
CXX=g++
CXX_FLAGS=-Wall ...
build_lib:
  $(CXX) $(CXX_FLAGS) -o lib lib.cc
build_main: build_lib
  $(CXX) $(CXX_FLAGS) -o main main.cc
build_test: build_lib
  $(CXX) $(CXX_FLAGS) -o test test.cc
test:
  ./test
```

---

### Pros:

- Is able to cache build targets
- Can parallelize build target (eg: `build_main` and `build_test/test`)
- Can also be used with any lanuage/platform

### Cons:

- As portable as a shell script
- Naive caching based on timestamp
- Hard to reuse tooling
- Hard to read

---

## CMake

```cmake
project(stuff)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall ...")

add_library(lib SHARED lib.cc)

add_executable(main main.cc)
target_link_libraries(main lib)

add_executable(test_bin test.cc)
target_link_libraries(test_bin lib)

add_custom_target(
  test 
  COMMAND ./test_bin
  DEPENDS test_bin)
```

---

### Pros:

- Reusable functions and macros
- Makes it easier to write portable build scripts
- Has good support for a bunch of compiled languages out-of-the-box
- Well integrated with 3rd party tooling
- Very configurable
- Someone wrote a raytracer with cmake: https://github.com/64/cmake-raytracer

### Cons:

- Still suffers from the same issue as the underlying build system

---

## Languge-specific build systems

##### Example: Maven

```xml
<project ... >
    <groupId>world.hello</groupId>
    <artifactId>hello-world</artifactId>
    <packaging>jar</packaging>
    <version>0.0.1</version>

    <properties>
        <maven.compiler.source>1.8</maven.compiler.source>
        <maven.compiler.target>1.8</maven.compiler.target>
    </properties>
</project>
```

---

### Pros:

- Drop-in solution for a specific language
- Easy to use
- Usually has support for dependency management out-of-the-box
- Very well integrated within the ecosystem

### Cons:

- Specific to a single language
- Hard to tune
- Hard to integrate different projects together

---

## What is Bazel?

- Open-source build system developed by Google
- Designed for large, complex software projects
- Scalable, deterministic, and supports multiple languages
- Uses Starlark build language
- Wide range of programming languages and platforms supported
- Built-in caching and distributed builds for faster and efficient builds

---

## Let's have a look

```python
cc_library(
  name="lib",
  srcs=["lib.cc"],
)

cc_binary(
  name="main",
  srcs=["main.cc"],
  deps=[":lib"],
)

cc_test(
  name="test",
  srcs=["test.cc"],
  deps=[":lib"],
)
```

---

### Pros:

- Works with a plethora of languages out-of-the-box
- Smarter and more reliable caching based on content hashing
- Very extendable
- Has its own dependency management: `blzmod`
- Optimised for speed and reproducibility
- Powerful toolchains system that makes build very portable
- Developed by Google

### Cons:

- Tooling support could improve
- Developed by Google

---


## Benefits of Bazel

- Scalability:
  - Incremental build system for faster builds
  - Avoids recompiling and retesting unchanged code

- Determinism:
  - Reproducible and hermetic builds
  - Consistent results across different environments

- Multi-language and Multi-platform Support:
  - Support for various languages and platforms
  - Eases development of polyglot projects

- Extensibility:
  - Customizable with Starlark language
  - Integration with existing tooling and frameworks

---

## Companies Using Bazel

- Google: Bazel was originally developed by Google and extensively used internally
- Uber: Utilizes Bazel for building and testing their large-scale codebase
- Dropbox: Manages complex codebase and improves build times with Bazel
- SpaceX: Relies on Bazel for rocket software development

---

## Conclusion

- Bazel provides a robust solution for large, complex software projects
- Addresses scalability, determinism, and multi-language support challenges
- Adoption by major companies demonstrates its effectiveness
- Consider adopting Bazel to improve efficiency, reliability, and productivity

---

## Questions?

---

## Thank You!

- Contact information:
  - Email: your.email@example.com
  - LinkedIn: linkedin.com/in/your-profile

- Additional resources:
  - Bazel official website: bazel.build
  - Bazel GitHub repository: github.com/bazelbuild/bazel

---

