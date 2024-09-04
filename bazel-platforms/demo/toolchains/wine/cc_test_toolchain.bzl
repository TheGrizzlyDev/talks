CcTestInfo = provider()
GetRunnerInfo = provider()

_WINE_RUN_TMPL_ARG_NAME = "wine-run-template-path"

def _get_test_runner(ctx, binary_info, processed_environment, **args):
    wrapper_script = ctx.actions.declare_file("run_test_with_wine.sh")
    ctx.actions.expand_template(
        template=args[_WINE_RUN_TMPL_ARG_NAME],
        output=wrapper_script,
        substitutions={
            "{WINEPREFIX}": "tmp_prefix",
            "{ARGS}": "{bin}".format(bin=binary_info.executable.short_path),
        },
        is_executable=True,
    )
    runfiles = ctx.runfiles([binary_info.executable]).merge(binary_info.runfiles)
    return [
        DefaultInfo(
            executable=wrapper_script,
            files=depset(direct=[wrapper_script], transitive=[binary_info.files]),
            runfiles=runfiles,
        )
    ]

def toolchain_wine_cc_test_impl(ctx):
    toolchain_info = platform_common.ToolchainInfo(
        cc_test_info = CcTestInfo(
            linkopts = [], # TODO not the best idea to hardcode this
            linkstatic = True, # TODO not the best idea to hardcode this
            get_runner = GetRunnerInfo(
                func = _get_test_runner,
                args = {
                    _WINE_RUN_TMPL_ARG_NAME: ctx.file._wine_run_sh_tmpl
                },
            )
        )
    )
    return [toolchain_info]


toolchain_wine_cc_testing = rule(
    toolchain_wine_cc_test_impl,
    attrs = {
        "_wine_run_sh_tmpl": attr.label(default = "//toolchains/wine:wine-run.tmpl.sh", allow_single_file=True),
    },
)
