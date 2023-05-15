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

- Efficiency: Minimize work during builds
- Reproducible Builds: Consistently generate results in any environment
- Configurability: Allow users to customize builds
- Multi-language and Multi-platform Support: Adapt to diverse ecosystems
- Integration with Tooling and Third-party Code: Seamless integration with popular tools and dependency management

---

# History of Build Systems

---

## Make
- Introduced in 1976
- Originally designed for building C programs
- Uses `Makefile` to define build targets and dependencies

---

## CMake
- Developed in 2000
- Cross-platform build system
- Generates native build files (e.g., Makefiles, Visual Studio projects)

---

## Maven
- Created in 2004
- Primarily used for Java projects
- Manages project dependencies and builds using declarative XML files

---

## Gradle
- Introduced in 2007
- Builds on the concepts of Apache Ant and Maven
- Supports multiple languages and flexible build configurations

---

## What is Bazel?

- Open-source build system developed by Google
- Designed for large, complex software projects
- Scalable, deterministic, and supports multiple languages
- Uses Starlark build language
- Wide range of programming languages and platforms supported
- Built-in caching and distributed builds for faster and efficient builds

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

