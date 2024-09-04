load("@bazel_tools//tools/build_defs/cc:action_names.bzl", "ACTION_NAMES")
load("@bazel_tools//tools/cpp:cc_toolchain_config_lib.bzl", "action_config", "tool", "feature", "flag_set", "flag_group")

def mingw_cc_toolchain_config_impl(ctx):
    action_configs = [
        action_config(
            action_name = ACTION_NAMES.c_compile,
            tools = [tool(path="bin/x86_64-w64-mingw32-gcc")],
        ),
        action_config(
            action_name = ACTION_NAMES.cpp_compile,
            tools = [tool(path="bin/x86_64-w64-mingw32-g++")],
        ),
        action_config(
            action_name = ACTION_NAMES.cpp_link_executable,
            tools = [tool(path="bin/x86_64-w64-mingw32-g++")],
            implies = [
                "no_stripping",
            ],
        ),
        action_config(
            action_name = ACTION_NAMES.cpp_link_static_library,
            tools = [tool(path="bin/x86_64-w64-mingw32-ar")],
            implies = [
                "archiver_flags",
            ],
        ),
    ]

    no_stripping_feature = feature(name = "no_stripping")

    default_linker_flags = feature(
        name = "default_linker_flags",
        enabled = True,
        flag_sets = [
            flag_set(
                actions = [ACTION_NAMES.cpp_link_executable],
                flag_groups = ([flag_group(flags = ["-static"])]),
            ),
        ],
    )

    features = [
        default_linker_flags,
        no_stripping_feature,
    ]

    return cc_common.create_cc_toolchain_config_info(
        ctx = ctx,
        features = features,
        toolchain_identifier = "k8-toolchain",
        host_system_name = "local",
        target_system_name = "local",
        target_cpu = "k8",
        target_libc = "unknown",
        compiler = "mingw",
        abi_version = "unknown",
        abi_libc_version = "unknown",
        action_configs = action_configs,
        cxx_builtin_include_directories = [
            # TODO figure out how to remove this
            "/home/antonio/.cache/bazel/_bazel_antonio/11619844efe16372c25298fcb26ed920/external/_main~_repo_rules~mingw_linux_x86_64_toolchain/lib/clang/19/include/",
            # "%sysroot%/lib/clang/19/include/",
            # "%sysroot%/x86_64-w64-mingw32/include/",
            # "%sysroot%/x86_64-w64-mingw32/include/c++/v1/",
        ],
        builtin_sysroot = "external/{repo}/"
    )

mingw_cc_toolchain_config = rule(
    implementation = mingw_cc_toolchain_config_impl,
    attrs = {},
    provides = [CcToolchainConfigInfo],
)