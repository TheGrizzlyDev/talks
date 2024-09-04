def _platform_transition_impl(settings, attr):
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

    return [
        DefaultInfo(executable=bin)
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