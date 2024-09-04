def _bootstrap_prefix_impl(ctx):
    zipped_prefix = ctx.actions.declare_file(ctx.attr.name + ".zip")
    
    ctx.actions.run_shell(
        outputs = [zipped_prefix],
        inputs = [],
        command = "WINEPREFIX=$(realpath {prefix}) xvfb-run wine cmd dir && ls -lisa && zip -r {zip} {prefix} && rm -r {prefix}".format(
            prefix=ctx.attr.name,
            zip=zipped_prefix.basename,
        ),
    )
    
    return DefaultInfo(files=depset([zipped_prefix]))

bootstrap_prefix = rule(_bootstrap_prefix_impl)