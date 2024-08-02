def unzip_7z_impl(ctx):
    toolchain_7z = ctx.toolchains["//toolchains/7zip:toolchain_type"]
    destination = ctx.actions.declare_directory(ctx.attr.name)
    ctx.actions.run(
        outputs = [destination],
        inputs = [ctx.file.archive],
        executable = toolchain_7z.executable.executable,
        arguments = [
            "x",
            ctx.file.archive.path,
            "-o%s" % destination.path,
        ],
    )
    return [
        DefaultInfo(
            files = depset([destination]),
        ),
    ]


unzip_7z = rule(
    unzip_7z_impl,
    attrs = {
        "archive": attr.label(allow_single_file=True),
    },
    toolchains = ["//toolchains/7zip:toolchain_type"],
)