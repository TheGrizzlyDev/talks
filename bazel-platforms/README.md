TODO:

- define valid toolchain of type: `@bazel_tools//tools/cpp:test_runner_toolchain_type`. Used by https://github.com/bazelbuild/bazel/blob/631bd85beeabe0e95288a0234536d75e7f772723/src/main/starlark/builtins_bzl/common/cc/cc_test.bzl#L30 and defined in https://github.com/bazelbuild/bazel/blob/631bd85beeabe0e95288a0234536d75e7f772723/tools/cpp/BUILD.tools#L23
- define a mingw cross-compiling C/C++ toolchain running on Linux
- define a gcc/clang cross-compiling C/C++ toolchain running on Windows
