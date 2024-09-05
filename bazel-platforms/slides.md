---
marp: true
---

![width:400px](./assets/logo_large_96px_w.png)

# A tour of Bazel's platform and toolchains

---

# Who am I?

```yaml
name: Antonio Di Stefano
role: Solution engineer @ EngFlow
goal: Build tools to make development more productive and enjoyable
likes: ['ducks', 'beer', 'travel', 'metal']
dislikes: ['yaml']
links:
    email: antonio@engflow.com
    github: https://github.com/TheGrizzlyDev
    linkedin: https://www.linkedin.com/in/antonio-di-stefano-405230108/
```

--- 

# What is this talk about?

- Bazel platforms and toolchains
- Cross-building and testing software with Bazel
- Creating hermetic builds

---

# What is Bazel?

- A fork of Google's internal build system - Blaze
- Engineered for speed, correctness and driving people crazy with flags
- Able to distribute actions (compilations, linking, tests, etc.) across multiple machines on the cloud - further speeding up builds

---

```python
cc_library( # <-- `cc_library` is a rule
    name = "lib", # <-- `lib` is a target 
    srcs = ["lib.cc"],
    hdrs = ["lib.hh"],
)

cc_binary(
    name = "bin",
    srcs = ["main.cc"],
    deps = [":lib"], # <-- `bin` depends on `lib`
)

cc_test( # <-- this target will generate a test
    name = "test"
    srcs = glob(["*_test.cc"]),
    deps = [":lib"],
)
```

---

# Platforms and constraints

- **Constraints**: a set of dimensions (like cpu architecture, OS, etc.) used to configure a build result or the build environment
- **Platform**: a collection of constraints that describes either:
    - **Target**: the system on which your software runs on
    - **Execution**: where actions like compiling and linking are being run (which could be your local machine on some remote instance if using remote execution)
    - **Host**: the machine you're running Bazel from. With local builds it coincides with the Execution platform

---

# What a platform looks like


```python

constraint_setting(name = "compiler")
constraint_value(name = "gcc", constraint_setting = ":glibc_version")
constraint_value(name = "mingw", constraint_setting = ":compiler")

platform(
    name = "linux_x86",
    constraint_values = [
        "@platforms//os:linux",
        "@platforms//cpu:x86_64",
        ":gcc",
    ],
)

platform(
    name = "win_x86",
    constraint_values = [
        "@platforms//os:windows",
        "@platforms//cpu:x86_64",
        ":mingw",
    ],
)
```

---

# Toolchains

- Set of tools needed to build a software, used by rules
- Can be restricted using constraints
- Can depend on the system or from artifacts fetched during the build (hermetic toolchains)
- Native rulesets have ad-hoc pre-existing toolchains


---

# Demo
## Building and testing an app for windows and linux using mingw and wine

---

# Q&A