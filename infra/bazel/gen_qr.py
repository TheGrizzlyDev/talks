#!/usr/bin/env python3
"""Encode a single URL (or arbitrary string) into a QR code PNG.

Usage: gen_qr.py --data STRING --output PATH [--box-size N] [--border N]
                 [--fill HEX] [--back HEX]
"""

import argparse
import sys

import qrcode


def main(argv):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", required=True, help="String to encode")
    p.add_argument("--output", required=True, help="Output PNG path")
    p.add_argument("--box-size", type=int, default=12)
    p.add_argument("--border", type=int, default=2)
    p.add_argument("--fill", default="#0B2E14",
                   help="Foreground color, hex or CSS name")
    p.add_argument("--back", default="white",
                   help="Background color, hex or CSS name")
    args = p.parse_args(argv[1:])

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=args.box_size,
        border=args.border,
    )
    qr.add_data(args.data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=args.fill, back_color=args.back)
    img.save(args.output)
    print(f"{args.output}: {img.size[0]}x{img.size[1]} -> {args.data}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
