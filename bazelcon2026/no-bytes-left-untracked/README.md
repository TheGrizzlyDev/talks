# No Bytes Left Untracked — BazelCon 2026

Deck for "No Bytes Left Untracked: Bazel Supply Chain Security".

## Build

Drop the EngFlow template into `template/BazelCon_Amst26_ppt.pptx` (not
versioned; grab it from the shared drive), then from the workspace root
(`~/src/talks/`):

```sh
bazel build //bazelcon2026/no-bytes-left-untracked:deck
```

Output: `bazel-bin/bazelcon2026/no-bytes-left-untracked/NoBytesLeftUntracked_BazelCon.pptx`.

## Layout

- `build_deck.py` — deck generator (python-pptx).
- `template/` — vendored EngFlow slide template.
- `BUILD.bazel` — one `qrcode()` target per URL, one `py_binary` for the
  builder, plus the `:deck` genrule that ties them together.

Shared infrastructure lives in `//infra/bazel`:
- `qrcode.bzl` — macro that emits a QR PNG for a string.
- `gen_qr.py` — underlying tool.

## Add a new QR code

```starlark
qrcode(
    name = "qr_myslack",
    data = "https://example.com/whatever",
)
```

Depend on `:qr_myslack` from any rule to pull in that PNG.
