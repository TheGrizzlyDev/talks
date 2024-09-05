def mingw_linux_toolchain_impl(repo_ctx):
    repo_ctx.download_and_extract(
        url=repo_ctx.attr.urls,
        sha256=repo_ctx.attr.sha256,
        stripPrefix=repo_ctx.attr.strip_prefix,
    )
    template_subs = {
        "{exec_os}": repo_ctx.attr.os,
        "{exec_arch}": repo_ctx.attr.arch,
        "{repo}": repo_ctx.name,
    }
    repo_ctx.template("BUILD.bazel", repo_ctx.attr._build_tmpl, substitutions=template_subs)
    repo_ctx.template("configure.bzl", repo_ctx.attr._configure_tmpl, substitutions=template_subs)


mingw_linux_toolchain = repository_rule(
    mingw_linux_toolchain_impl,
    attrs = {
        "os": attr.string(),
        "arch": attr.string(),
        "sha256": attr.string(),
        "strip_prefix": attr.string(),
        "urls": attr.string_list(),
        "_build_tmpl": attr.label(default = "//toolchains/mingw:BUILD.mingw.tmpl.bzl"),
        "_configure_tmpl": attr.label(default = "//toolchains/mingw:configure.tmpl.bzl"),
    }
)