Toolchain7ZipInfo = provider()

def toolchain_7z_impl(ctx):
    toolchain_info = platform_common.ToolchainInfo(
        executable = Toolchain7ZipInfo(
            executable = ctx.file.exe,
        ),
    )
    return [toolchain_info]


toolchain_7z = rule(
    toolchain_7z_impl,
    attrs = {
        "exe": attr.label(allow_single_file=True, executable=True, cfg="exec"),
    },
)
