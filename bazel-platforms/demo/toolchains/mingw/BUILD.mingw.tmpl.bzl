load(":configure.bzl", "mingw_cc_toolchain_config")

filegroup(
    name = "all_srcs",
    srcs = glob(["**/*"]),
)

mingw_cc_toolchain_config(
    name = "toolchain_config"
)

# https://github.com/bazelbuild/bazel/blob/master/src/main/starlark/builtins_bzl/common/cc/cc_toolchain.bzl
cc_toolchain(
    name = "cc_toolchain",
    toolchain_identifier = "mingw_{exec_os}_{exec_arch}",
    toolchain_config = ":toolchain_config",
    all_files = ":all_srcs",
    ar_files = ":all_srcs",
    compiler_files = ":all_srcs",
    dwp_files = ":all_srcs",
    linker_files = ":all_srcs",
    objcopy_files = ":all_srcs",
    strip_files = ":all_srcs",
    supports_param_files = 0,
)

toolchain(
    name = "toolchain",
    toolchain = ":cc_toolchain",
    toolchain_type = "@bazel_tools//tools/cpp:toolchain_type",
    exec_compatible_with = [
        "@platforms//cpu:{exec_arch}",
        "@platforms//os:{exec_os}",
    ],
    target_compatible_with = [
        "@platforms//cpu:x86_64",
        "@platforms//os:windows",
    ],
)