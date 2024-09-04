_SUPPORTED_PLATFORMS = [
    "//platforms:win_amd64_mingw",
    "//platforms:linux_amd64_gcc",
]

def _platform_transition_impl(settings, attr):
    # TODO use supported platforms
    return {
        "//platforms:linux_amd64_gcc": {
            "//command_line_option:platforms": "//platforms:linux_amd64_gcc",
        },
        "//platforms:win_amd64_mingw": {
            "//command_line_option:platforms": "//platforms:win_amd64_mingw",
        },
    }

platform_transition = transition(
    implementation = _platform_transition_impl,
    inputs = [],
    outputs = ["//command_line_option:platforms"]
)

def transition_for_default_info(ctx):
    target = ctx.split_attr.dep[ctx.attr.platform]
    bin = ctx.actions.declare_file(ctx.attr.name)
    ctx.actions.symlink(output=bin, target_file=target[DefaultInfo].files_to_run.executable, is_executable=True)
    runfiles = ctx.runfiles([target[DefaultInfo].files_to_run.executable]).merge(target[DefaultInfo].default_runfiles)

    return [
        DefaultInfo(
            executable=bin,
            files=depset(transitive=[target[DefaultInfo].files]),
            runfiles=runfiles,
        )
    ]

def _transition_binary_impl(ctx):
    return transition_for_default_info(ctx)
    

transition_binary = rule(
    _transition_binary_impl,
    executable=True,
    attrs = {
        "dep": attr.label(cfg=platform_transition),
        "platform": attr.string(),
    }
)

def _transition_test_impl(ctx):
    return transition_for_default_info(ctx)

transition_test = rule(
    _transition_test_impl,
    executable=True,
    test=True,
    attrs = {
        "dep": attr.label(cfg=platform_transition),
        "platform": attr.string(),
    }
)

def nameify_platform_label(label):
    return label.replace("//", "root_").replace(":", "_").replace("@", "repo_")

def multi_platform_cc_binary(name, **kwargs):
    binary_name = name + ".exe"
    native.cc_binary(
        # because mingw will unconditionally append a .exe extension to files, 
        # this way the file name matches the one bazel expect as an output
        name=binary_name,
        **kwargs,
    )

    transition_targets = []
    for platform in _SUPPORTED_PLATFORMS:
        transition_target_name = nameify_platform_label(platform) + name
        transition_targets.append(transition_target_name)
        transition_binary(
            name=transition_target_name,
            dep=binary_name,
            platform=platform,
        )
    
    native.filegroup(
        name=name,
        srcs=transition_targets,
        data=transition_targets,
    )

    

def multi_platform_cc_test(name, **kwargs):
    binary_name = name + ".exe"
    native.cc_test(
        # because mingw will unconditionally append a .exe extension to files, 
        # this way the file name matches the one bazel expect as an output
        name=binary_name,
        **kwargs,
    )

    for platform in _SUPPORTED_PLATFORMS:
        transition_target_name = nameify_platform_label(platform) + name
        transition_test(
            name=transition_target_name,
            dep=binary_name,
            platform=platform,
        )