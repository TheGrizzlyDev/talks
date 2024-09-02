load("@bazel_tools//tools/cpp:cc_toolchain_config_lib.bzl", "tool_path")

def mingw_cc_toolchain_config_impl(ctx):
    tool_paths = [
        tool_path(
            name = "gcc",
            path = "/usr/bin/x86_64-w64-mingw32-gcc",
        ),
        tool_path(
            name = "ld",
            path = "/usr/bin/x86_64-w64-mingw32-ld",
        ),
        tool_path(
            name = "ar",
            path = "/usr/bin/ar",
        ),
        tool_path(
            name = "cpp",
            path = "/usr/bin/x86_64-w64-mingw32-g++",
        ),
        tool_path(
            name = "gcov",
            path = "/bin/false",
        ),
        tool_path(
            name = "nm",
            path = "/bin/false",
        ),
        tool_path(
            name = "objdump",
            path = "/bin/false",
        ),
        tool_path(
            name = "strip",
            path = "/bin/false",
        ),
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
            "/usr/share/mingw-w64/include/",
            "/usr/lib/gcc/x86_64-w64-mingw32/10-win32/include/c++/",
            "/usr/lib/gcc/x86_64-w64-mingw32/10-win32/include/",
            "/usr/lib/gcc/x86_64-w64-mingw32/10-win32/include-fixed/",
        ],
    )

mingw_cc_toolchain_config = rule(
    implementation = mingw_cc_toolchain_config_impl,
    attrs = {},
    provides = [CcToolchainConfigInfo],
)