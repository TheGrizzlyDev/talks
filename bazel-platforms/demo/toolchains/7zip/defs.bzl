def unzip_7z_impl(ctx):
    toolchain_7z = ctx.toolchains["//toolchains/7zip:toolchain_type"]
    destination = ctx.actions.declare_directory(ctx.attr.name)
    toolchain_7z.toolchain_7zip_info.unzip(ctx, ctx.file.archive, destination)
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