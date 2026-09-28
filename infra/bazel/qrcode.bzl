"""Macro that emits a single QR-code PNG from a string."""

_GEN_QR = "//infra/bazel:gen_qr"

def qrcode(name, data, out = None, **kwargs):
    """Encode `data` into a QR PNG named `out` (default `<name>.png`)."""
    out = out or (name + ".png")
    native.genrule(
        name = name,
        outs = [out],
        cmd = "$(execpath {tool}) --data '{data}' --output $@".format(
            tool = _GEN_QR,
            data = data.replace("'", "'\\''"),
        ),
        tools = [_GEN_QR],
        **kwargs
    )
