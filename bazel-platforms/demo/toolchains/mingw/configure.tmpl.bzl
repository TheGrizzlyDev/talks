load("@bazel_tools//tools/cpp:cc_toolchain_config_lib.bzl", "tool_path")

def mingw_cc_toolchain_config_impl(ctx):
    tool_paths = [
        tool_path(name = tool, path = "bin/x86_64-w64-mingw32-{tool}".format(tool=tool))
        for tool in [
            "gcc",
            "ld",
            "ar",
            "g++",
            "cpp",
            "gcov",
            "nm",
            "objdump",
            "strip",
        ]
    ]
    return cc_common.create_cc_toolchain_config_info(
        ctx = ctx,
        toolchain_identifier = "k8-toolchain",
        host_system_name = "local",
        target_system_name = "local",
        target_cpu = "k8",
        target_libc = "unknown",
        compiler = "mingw",
        abi_version = "unknown",
        abi_libc_version = "unknown",
        tool_paths = tool_paths,
        cxx_builtin_include_directories = [
            "x86_64-w64-mingw32/include",
            "x86_64-w64-mingw32/include/c++/v1",
        ],
    )

mingw_cc_toolchain_config = rule(
    implementation = mingw_cc_toolchain_config_impl,
    attrs = {},
    provides = [CcToolchainConfigInfo],
)