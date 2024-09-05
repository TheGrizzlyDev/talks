Toolchain7ZipInfo = provider()

def unzip_builder(bin):
    def unzip(ctx, source, destination):
        ctx.actions.run(
            outputs = [destination],
            inputs = [source],
            executable = bin,
            arguments = [
                "x",
                source.path,
                "-o%s" % destination.path,
            ],
        )
    return unzip

def zip_builder(bin):
    def unzip(ctx, archive, srcs):
        ctx.actions.run(
            outputs = [archive],
            inputs = srcs,
            executable = bin,
            arguments = [
                "a",
                archive.path
            ] + [src.path for src in srcs],
        )
    return unzip
    

def toolchain_7z_impl(ctx):
    toolchain_info = platform_common.ToolchainInfo(
        toolchain_7zip_info = Toolchain7ZipInfo(
            unzip = unzip_builder(ctx.file.exe),
            zip = zip_builder(ctx.file.exe),
        ),
    )
    return [toolchain_info]


toolchain_7z = rule(
    toolchain_7z_impl,
    attrs = {
        "exe": attr.label(allow_single_file=True, executable=True, cfg="exec"),
    },
)
