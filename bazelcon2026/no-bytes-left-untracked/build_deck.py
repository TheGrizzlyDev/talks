#!/usr/bin/env python3
"""Build the 'No Bytes Left Untracked' BazelCon deck from the EngFlow template.

Usage: build_deck.py --template PATH --qr-dir DIR --output PATH
"""

import argparse
import os
import sys

from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from lxml import etree

_parser = argparse.ArgumentParser(description=__doc__)
_parser.add_argument("--template", required=True, help="Input .pptx template")
_parser.add_argument("--output", required=True, help="Output .pptx path")
_parser.add_argument("--qr-repo", required=True, help="QR PNG for the repo link")
_parser.add_argument("--qr-valact", required=True, help="QR PNG for validation actions doc")
_parser.add_argument("--qr-bof", required=True, help="QR PNG for the BoF session")
_args = _parser.parse_args()

TEMPLATE = _args.template
OUTPUT = _args.output
QR_REPO = _args.qr_repo
QR_VALACT = _args.qr_valact
QR_BOF = _args.qr_bof

A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"

WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BRIGHT_GREEN = RGBColor(0x7E, 0xC4, 0x74)
ACCENT_GREEN = RGBColor(0x8D, 0xC5, 0x3F)
CODE_BG = RGBColor(0x0B, 0x2E, 0x14)
CODE_TEXT = RGBColor(0xF5, 0xF5, 0xF5)
LIGHT_GREY = RGBColor(0xDD, 0xE8, 0xDD)
NODE_FILL = RGBColor(0x0B, 0x70, 0x39)
NODE_BORDER = RGBColor(0x7E, 0xC4, 0x74)


def clear_deck(prs):
    sldIdLst = prs.slides._sldIdLst
    rId_to_drop = []
    for sldId in list(sldIdLst):
        rId_to_drop.append(sldId.get(
            "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"))
        sldIdLst.remove(sldId)
    part = prs.part
    for rId in rId_to_drop:
        try:
            part.drop_rel(rId)
        except Exception:
            pass


def clear_tf(tf):
    txBody = tf._txBody
    for p in txBody.findall(f"{{{A_NS}}}p"):
        txBody.remove(p)
    etree.SubElement(txBody, f"{{{A_NS}}}p")


def set_run(run, size=None, bold=None, color=None, font="Arial", italic=None):
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if italic is not None:
        run.font.italic = italic
    if color is not None:
        run.font.color.rgb = color
    if font is not None:
        run.font.name = font


LEVEL_INDENT_EMU = {
    0: (457200, -342900),
    1: (914400, -342900),
    2: (1371600, -342900),
}


def add_paragraph(tf, text, *, size=18, bold=False, color=WHITE,
                  level=0, bullet=True, bullet_color=None,
                  align=None, italic=False, first=False,
                  font="Arial"):
    """Add a paragraph. Explicitly manages bullet color and per-level indent so
    the output looks the same in placeholders and free-standing textboxes."""
    if first and len(tf.paragraphs) == 1 and not tf.paragraphs[0].runs:
        p = tf.paragraphs[0]
    else:
        p = tf.add_paragraph()

    p.level = level
    if align is not None:
        p.alignment = align

    pPr = p._p.get_or_add_pPr()
    for tag in ("buClr", "buChar", "buAutoNum", "buNone", "buFont",
                "buSzPts", "buSzPct"):
        for el in pPr.findall(f"{{{A_NS}}}{tag}"):
            pPr.remove(el)

    # Explicit indent per level so nesting is visible in any container
    marL, indent = LEVEL_INDENT_EMU.get(level, LEVEL_INDENT_EMU[0])
    pPr.set("marL", str(marL))
    pPr.set("indent", str(indent))

    if bullet:
        bc = bullet_color if bullet_color is not None else color
        buClr = etree.SubElement(pPr, f"{{{A_NS}}}buClr")
        srgb = etree.SubElement(buClr, f"{{{A_NS}}}srgbClr")
        srgb.set("val", "{:02X}{:02X}{:02X}".format(bc[0], bc[1], bc[2]))
        buFont = etree.SubElement(pPr, f"{{{A_NS}}}buFont")
        buFont.set("typeface", "Arial")
        buChar = etree.SubElement(pPr, f"{{{A_NS}}}buChar")
        buChar.set("char", "●" if level == 0 else ("○" if level == 1 else "■"))
    else:
        # No bullet + no hanging indent
        pPr.set("marL", "0")
        pPr.set("indent", "0")
        etree.SubElement(pPr, f"{{{A_NS}}}buNone")

    run = p.add_run()
    run.text = text
    set_run(run, size=size, bold=bold, color=color, italic=italic, font=font)
    return p


def add_title(slide, title_text, *, size=28, color=WHITE, bold=True):
    for ph in slide.placeholders:
        if ph.placeholder_format.idx == 0:
            tf = ph.text_frame
            clear_tf(tf)
            add_paragraph(tf, title_text, size=size, bold=bold, color=color,
                          bullet=False, first=True)
            return ph
    return None


def add_body_bullets(slide, items, *, ph_idx=1, base_size=18, color=WHITE,
                     bullet_color=None):
    ph = None
    for p in slide.placeholders:
        if p.placeholder_format.idx == ph_idx:
            ph = p
            break
    if ph is None:
        return
    tf = ph.text_frame
    tf.word_wrap = True
    clear_tf(tf)
    first = True
    for it in items:
        text, level = (it if isinstance(it, tuple) else (it, 0))
        size = base_size if level == 0 else max(12, base_size - 3)
        add_paragraph(tf, text, size=size, level=level, bullet=True,
                      color=color, bullet_color=bullet_color or color,
                      first=first)
        first = False


def add_textbox(slide, left, top, width, height, lines, *,
                fill=None, font_size=12, color=CODE_TEXT, mono=True, bold=False,
                align=None):
    tb = slide.shapes.add_textbox(Emu(left), Emu(top), Emu(width), Emu(height))
    if fill is not None:
        tb.fill.solid()
        tb.fill.fore_color.rgb = fill
    else:
        tb.fill.background()
    tb.line.fill.background()
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Emu(91425)
    tf.margin_right = Emu(91425)
    tf.margin_top = Emu(45700)
    tf.margin_bottom = Emu(45700)
    clear_tf(tf)
    first = True
    for line in lines:
        p = add_paragraph(tf, line, size=font_size, color=color, bullet=False,
                          bold=bold, align=align, first=first,
                          font=("Courier New" if mono else "Arial"))
        first = False
    return tb


def add_bullets_textbox(slide, left, top, width, height, bullets, *,
                       base_size=16, color=WHITE, bullet_color=None):
    tb = slide.shapes.add_textbox(Emu(left), Emu(top), Emu(width), Emu(height))
    tb.fill.background()
    tb.line.fill.background()
    tf = tb.text_frame
    tf.word_wrap = True
    clear_tf(tf)
    first = True
    for it in bullets:
        text, level = (it if isinstance(it, tuple) else (it, 0))
        size = base_size if level == 0 else max(12, base_size - 3)
        add_paragraph(tf, text, size=size, level=level, bullet=True,
                      color=color, bullet_color=bullet_color or color,
                      first=first)
        first = False
    return tb


def add_diagram_node(slide, left, top, width, height, text, *,
                     fill=NODE_FILL, border=NODE_BORDER, text_color=WHITE,
                     font_size=14, bold=True):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                Emu(left), Emu(top), Emu(width), Emu(height))
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.line.color.rgb = border
    sh.line.width = Pt(1.5)
    tf = sh.text_frame
    tf.word_wrap = True
    tf.margin_left = Emu(45700)
    tf.margin_right = Emu(45700)
    tf.margin_top = Emu(45700)
    tf.margin_bottom = Emu(45700)
    clear_tf(tf)
    add_paragraph(tf, text, size=font_size, bold=bold, color=text_color,
                  bullet=False, align=PP_ALIGN.CENTER, first=True)
    return sh


def add_arrow(slide, x1, y1, x2, y2, color=BRIGHT_GREEN):
    conn = slide.shapes.add_connector(3,  # MSO_CONNECTOR.STRAIGHT
                                       Emu(x1), Emu(y1), Emu(x2), Emu(y2))
    conn.line.color.rgb = color
    conn.line.width = Pt(2.5)
    # Add arrowhead at end
    ln = conn.line._get_or_add_ln()
    tailEnd = etree.SubElement(ln, f"{{{A_NS}}}tailEnd")
    tailEnd.set("type", "triangle")
    tailEnd.set("w", "med")
    tailEnd.set("h", "med")
    return conn


def add_qr_with_label(slide, qr_path, left, top, size, label, *,
                      label_size=11, label_color=WHITE, label_bold=True,
                      label_width=None):
    """Add a QR image at (left, top) with size x size, plus a centered label
    directly underneath. Sizes and positions are in EMU."""
    slide.shapes.add_picture(qr_path, Emu(left), Emu(top), Emu(size), Emu(size))
    lw = label_width if label_width is not None else size
    lleft = left + (size - lw) // 2
    ltop = top + size + 60000
    tb = slide.shapes.add_textbox(Emu(lleft), Emu(ltop), Emu(lw), Emu(400000))
    tb.fill.background(); tb.line.fill.background()
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = Emu(0); tf.margin_right = Emu(0)
    tf.margin_top = Emu(30000); tf.margin_bottom = Emu(0)
    clear_tf(tf)
    add_paragraph(tf, label, size=label_size, bold=label_bold,
                  color=label_color, bullet=False,
                  align=PP_ALIGN.CENTER, first=True)


def strip_handle(slide):
    for sh in list(slide.shapes):
        if sh.has_text_frame and "@handle" in sh.text_frame.text:
            sh._element.getparent().remove(sh._element)


# ------------------------------- Build deck -------------------------------

prs = Presentation(TEMPLATE)
clear_deck(prs)

L_TITLE = prs.slide_layouts[0]
L_SECTION = prs.slide_layouts[1]
L_BODY = prs.slide_layouts[2]
L_TITLE_ONLY = prs.slide_layouts[4]


# ---------- Slide 1: Title ----------
s = prs.slides.add_slide(L_TITLE)
strip_handle(s)
for ph in s.placeholders:
    if ph.placeholder_format.idx == 0:
        tf = ph.text_frame
        clear_tf(tf)
        add_paragraph(tf, "No Bytes Left Untracked", size=44, bold=True,
                      color=WHITE, bullet=False, first=True)
        add_paragraph(tf, "Bazel Supply Chain Security", size=25,
                      color=WHITE, bullet=False)
    elif ph.placeholder_format.idx == 1:
        tf = ph.text_frame
        clear_tf(tf)
        add_paragraph(tf, "Antonio Di Stefano · Yannic Bonenberger",
                      size=18, bold=True, color=WHITE, bullet=False, first=True)


# ---------- Slide 2: Why we all need to care ----------
s = prs.slides.add_slide(L_BODY)
add_title(s, "Why we should all care")
add_body_bullets(s, [
    ("High frequency of supply-chain attacks: xz, npm, SolarWinds, ...", 0),
    ("\"Correct\" builds aren't sufficient anymore, we need to prove what went into production", 1),
    ("Regulatory mandates: EO 14028, EU CRA", 0),
    ("Guidlines: SLSA", 0),
    ("SBOMs went from nice-to-have to legal requirement for software", 1),
    ("Bazel already knows everything about the build", 0),
    ("That target graph is an SBOM waiting to be emitted", 1),
], base_size=18)


# ---------- Slide 3: The status quo falls short ----------
s = prs.slides.add_slide(L_BODY)
add_title(s, "The status quo often falls short")
add_body_bullets(s, [
    ("Ecosystem manifests are siloed", 0),
    ("pom.xml, go.mod, package.json, Cargo.toml. One per language", 1),
    ("Post-hoc scanners guess at what the build actually consumed", 0),
    ("The truth is in the action graph. We should read it there", 1),
    ("Organizations are increasingly moving to polyglot monorepos", 0),
    ("Consistent tooling for provenence and conformance across ecosystems is a must", 1),
    ("Patching Bazel modules to add the necessary metadata is tedious", 0),
], base_size=18)


# ---------- Slide 4: The Supply-Chain SIG ----------
s = prs.slides.add_slide(L_TITLE_ONLY)
add_title(s, "The Supply-Chain SIG")
# Bullets on the left, QR on the right
add_bullets_textbox(s, 311700, 1000000, 6400000, 3700000, [
    ("Successor to rules_license", 0),
    ("Slack: #supply-chain-security on bazelbuild", 0),
    ("Weekly meeting: Thursdays, 8:30 EST / 14:30 CET", 0),
    ("Modules", 0),
    ("@package_metadata: core rule and providers", 1),
    ("@package_metadata_extensions: overrides and helpers", 1),
    ("@supply_chain_tools: Starlark tooling to emit SBOMs in standard formats", 1),
    ("@supply-chain-go: Go tools that generate the final SBOM artifact (SPDX, CycloneDX)", 1),
], base_size=15, color=WHITE)
add_qr_with_label(s, QR_REPO,
                  left=7100000, top=1300000, size=1700000,
                  label="bazel-contrib/supply-chain",
                  label_size=11, label_width=1900000)


# ---------- Slide 5: Headline @package_metadata 1.0 ----------
s = prs.slides.add_slide(L_TITLE_ONLY)
add_title(s, "@package_metadata v1.0", size=44)
# Center a subtitle + bullet block underneath the title
tb = s.shapes.add_textbox(Emu(311700), Emu(1500000), Emu(8520600), Emu(600000))
tb.fill.background(); tb.line.fill.background()
tf = tb.text_frame; tf.word_wrap = True
clear_tf(tf)

# Three "cards" horizontally
card_w = 2650000
card_h = 1900000
card_top = 2400000
gap = 200000
total_w = 3 * card_w + 2 * gap
start_left = (9144000 - total_w) // 2

cards = [
    ("Stable public API", "Safe to depend on. No breaking changes."),
    ("Extensible", "Many customization points so that organizations can meet their requirements."),
    ("Comprehensive docs", "Easy to get started."),
]
for i, (heading, body) in enumerate(cards):
    left = start_left + i * (card_w + gap)
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                            Emu(left), Emu(card_top), Emu(card_w), Emu(card_h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = NODE_FILL
    sh.line.color.rgb = BRIGHT_GREEN
    sh.line.width = Pt(1.5)
    tf = sh.text_frame
    tf.word_wrap = True
    tf.margin_left = Emu(120000); tf.margin_right = Emu(120000)
    tf.margin_top = Emu(120000); tf.margin_bottom = Emu(120000)
    clear_tf(tf)
    add_paragraph(tf, heading, size=18, bold=True, color=WHITE,
                  bullet=False, align=PP_ALIGN.CENTER, first=True)
    add_paragraph(tf, "", size=8, bullet=False, align=PP_ALIGN.CENTER)
    for line in body.split("\n"):
        add_paragraph(tf, line, size=13, color=WHITE, bullet=False,
                      align=PP_ALIGN.CENTER)


# ---------- Slide 6: Mental model (diagram) ----------
s = prs.slides.add_slide(L_TITLE_ONLY)
add_title(s, "Mental model")

# Four horizontal nodes with arrows in between
node_w = 1950000
node_h = 950000
node_top = 1700000
arrow_gap = 180000
total_w = 4 * node_w + 3 * arrow_gap
start = (9144000 - total_w) // 2

labels = [
    ("Target graph", "your BUILD files"),
    ("gather aspect", "gather_metadata_info"),
    ("Transitive info", "TransitiveMetadataInfo"),
    ("SBOM / policy", "SPDX, CycloneDX, checks"),
]

positions = []
for i, (heading, sub) in enumerate(labels):
    left = start + i * (node_w + arrow_gap)
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                            Emu(left), Emu(node_top), Emu(node_w), Emu(node_h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = NODE_FILL
    sh.line.color.rgb = BRIGHT_GREEN
    sh.line.width = Pt(1.5)
    tf = sh.text_frame; tf.word_wrap = True
    tf.margin_left = Emu(45000); tf.margin_right = Emu(45000)
    tf.margin_top = Emu(80000); tf.margin_bottom = Emu(80000)
    clear_tf(tf)
    add_paragraph(tf, heading, size=14, bold=True, color=WHITE,
                  bullet=False, align=PP_ALIGN.CENTER, first=True)
    add_paragraph(tf, sub, size=10, color=WHITE,
                  bullet=False, align=PP_ALIGN.CENTER)
    positions.append((left, node_top, node_w, node_h))

# Arrows between nodes
for i in range(len(positions) - 1):
    l, t, w, h = positions[i]
    l2, t2, w2, h2 = positions[i + 1]
    y = t + h // 2
    add_arrow(s, l + w, y, l2, y, color=BRIGHT_GREEN)

# Caption below the diagram
tb = s.shapes.add_textbox(Emu(311700), Emu(3000000), Emu(8520600), Emu(1400000))
tb.fill.background(); tb.line.fill.background()
tf = tb.text_frame; tf.word_wrap = True
clear_tf(tf)
add_paragraph(tf,
              "Metadata is a Bazel provider, propagated by an aspect. No side channels.",
              size=18, color=WHITE, bullet=False, align=PP_ALIGN.CENTER, first=True)
add_paragraph(tf, "", size=6, bullet=False)
add_paragraph(tf,
              "One rule to declare. One aspect to gather. One tool to emit.",
              size=18, color=WHITE, bullet=False, align=PP_ALIGN.CENTER)
add_paragraph(tf, "", size=6, bullet=False)
add_paragraph(tf,
              "The same primitives feed SPDX, CycloneDX, and your own policy checks.",
              size=16, color=WHITE, italic=True, bullet=False,
              align=PP_ALIGN.CENTER)


# ---------- Slide 7: The core rule: package_metadata ----------
s = prs.slides.add_slide(L_TITLE_ONLY)
add_title(s, "The core rule: package_metadata")

code_lines = [
    'load("@package_metadata//rules:package_metadata.bzl", "package_metadata")',
    "",
    "package_metadata(",
    '    name = "metadata",',
    '    purl = "pkg:generic/acme/widget@1.2.3",',
    "    attributes = [",
    '        ":owner_platform_team",',
    '        "@package_metadata//licenses/spdx:Apache-2.0",',
    "    ],",
    ")",
]
add_textbox(s, left=311700, top=1000000, width=8520600, height=2100000,
            lines=code_lines, fill=CODE_BG, font_size=13,
            color=CODE_TEXT, mono=True)

add_bullets_textbox(s, 311700, 3200000, 8520600, 1600000, [
    "purl is required. Canonical identity of the (third-party) package",
    "attributes is an open list of additional metadata (license, copyright, ...)",
    "Emits a metadata file plus dedicated attribute files (JSON)",
], base_size=16, color=WHITE)


# ---------- Slide 8: The providers ----------
s = prs.slides.add_slide(L_BODY)
add_title(s, "The providers")
add_body_bullets(s, [
    ("PackageMetadataInfo. What a package declares about itself", 0),
    ("PackageAttributeInfo. Extensible attribute kinds (license, copyright, owner, ...)", 0),
    ("PackageMetadataOverrideInfo. Inject metadata onto targets you don't own", 0),
    ("PackageMetadataToolchainInfo. Pluggable policy and toolchain", 0),
    ("TransitiveMetadataInfo. What the gathering aspect produces", 0),
], base_size=17)


# ---------- Slide 9: Extensibility #1: overrides ----------
s = prs.slides.add_slide(L_BODY)
add_title(s, "Extensibility #1: package_metadata_override")
add_body_bullets(s, [
    ("Ships in @package_metadata_extensions", 0),
    ("Rulesets are the primary place metadata lives", 0),
    ("Most of the time they provide PackageMetadataInfo directly on their targets", 1),
    ("Override is the escape hatch, useful when:", 0),
    ("A package manager isn't a first-class citizen of the ruleset", 1),
    ("There is no package manager at all (common in C++)", 1),
    ("Upstream attributes don't align with how your legal team classifies them", 1),
    ("Repo-wide defaults plus per-target overrides. No fork of the ruleset needed", 0),
], base_size=16)


# ---------- Slide 10: Extensibility #2: New attribute kinds ----------
s = prs.slides.add_slide(L_TITLE_ONLY)
add_title(s, "Extensibility #2: organization-specific attributes")

add_bullets_textbox(s, 311700, 1000000, 4200000, 3600000, [
    ("Extend by adding attribute kinds carried in PackageMetadataInfo.attributes", 0),
    ("No new top-level providers, no ruleset fork", 1),
    ("Each attribute target implements PackageAttributeInfo with its own kind", 0),
    ("e.g. license, owner, criticality, export_control", 1),
    ("The gathering aspect groups attributes by kind", 0),
    ("Custom kinds flow through unchanged", 1),
    ("Policy and SBOM code read them off TransitiveMetadataInfo", 0),
], base_size=14, color=WHITE)

code_lines = [
    "# file: criticality.bzl",
    "def _criticality_impl(ctx):",
    "    return [",
    "        PackageAttributeInfo(",
    '            kind = "com.example.criticality",',
    "            attributes = ctx.file.disclaimer,",
    "        ),",
    "    ]",
    "",
    "# file: BUILD | BUILD.bazel",
    "criticality(",
    '    name = "tier-1",',
    '    disclaimer = "tier-1.txt",',
    ")",
    "package_metadata(",
    '    name = "metadata",',
    '    purl = "pkg:generic/acme/widget@1.2.3",',
    "    attributes = [",
    '        ":owner_platform_team",',
    '        "//compliance/criticality:tier-1",',
    '        "//compliance/license:commecial-3",',
    "    ],",
    ")",
]
add_textbox(s, left=4700000, top=1000000, width=4200000, height=3600000,
            lines=code_lines, fill=CODE_BG, font_size=10,
            color=CODE_TEXT, mono=True)


# ---------- Slide 11: The gathering aspect ----------
s = prs.slides.add_slide(L_BODY)
add_title(s, "The gathering aspect")
add_body_bullets(s, [
    ("gather_metadata_info walks the graph from a root target", 0),
    ("Produces TransitiveMetadataInfo. The full dependency set with metadata", 0),
    ("Serialized to a canonical .graph.json", 0),
    ("A single source of truth for every downstream tool", 1),
    ("SBOMs, policy checks, and dashboards all read the same artifact", 0),
], base_size=18)


# ---------- Slide 12: SBOM generation ----------
s = prs.slides.add_slide(L_TITLE_ONLY)
add_title(s, "SBOM generation. Two formats, one graph")

code_lines = [
    'load("@supply_chain_tools//sbom:sbom.bzl", "sbom")',
    'load("@supply_chain_tools//sbom:spdx.bzl", "spdx")',
    'load("@supply_chain_tools//sbom:cyclonedx.bzl", "cyclonedx")',
    "",
    'sbom(name = "widget_sbom",  target = "//widget:bin")',
    'spdx(name = "widget_spdx",  sbom = ":widget_sbom", format = "json")',
    'cyclonedx(name = "widget_cdx", sbom = ":widget_sbom", format = "json")',
]
add_textbox(s, left=311700, top=1000000, width=8520600, height=1900000,
            lines=code_lines, fill=CODE_BG, font_size=13,
            color=CODE_TEXT, mono=True)

add_bullets_textbox(s, 311700, 3050000, 8520600, 1900000, [
    "sbom emits graph.json plus sbom-classifications.json (via @supply-chain-go//cmd/sbom)",
    "spdx: json, yaml, tag-value",
    "cyclonedx: json, xml",
    "Same graph feeds every emitter. No re-scanning, no drift between formats",
], base_size=15, color=WHITE)


# ---------- Slide 13: Policy checks as validation actions ----------
s = prs.slides.add_slide(L_TITLE_ONLY)
add_title(s, "Policy checks as validation actions")
add_bullets_textbox(s, 311700, 1000000, 6400000, 3700000, [
    ("Metadata is a provider, but attribute content lives in files", 0),
    ("Not readable at analysis time, so fail() from an aspect is not an option", 1),
    ("Enforce with validation actions instead", 0),
    ("An aspect declares an action whose output gates the build", 1),
    ("The action reads the .graph.json and exits non-zero on violations", 1),
    ("Examples", 0),
    ("Ban a license class from production binaries", 1),
    ("Require an owner attribute on anything you ship", 1),
    ("Block targets that are missing a PURL", 1),
], base_size=15, color=WHITE)
add_qr_with_label(s, QR_VALACT,
                  left=7100000, top=1300000, size=1700000,
                  label="bazel.build/extending/rules\n#validation-actions",
                  label_size=10, label_width=1900000)


# ---------- Slide 14: Demo ----------
s = prs.slides.add_slide(L_BODY)
add_title(s, "Demo")
add_body_bullets(s, [
    ("Polyglot repo: Java and Go", 0),
    ("Add package_metadata to first-party code", 0),
    ("Use package_metadata_override where a dep's attributes need adjusting", 0),
    ("e.g. license needs re-classifying, or the ruleset doesn't yet emit metadata", 1),
    ("bazel build //:widget_spdx //:widget_cdx", 0),
    ("Inspect both outputs side by side", 1),
], base_size=17)


# ---------- Slide 15: Adoption playbook ----------
s = prs.slides.add_slide(L_TITLE_ONLY)
add_title(s, "Adoption depends on your repo")

# Two columns: ruleset authors vs end users
col_w = 4100000
col_h = 3400000
col_top = 1050000
left_col = 311700
right_col = 311700 + col_w + 300000

for left, header, bullets in [
    (left_col, "If you maintain a ruleset", [
        "Tag your own dependencies with package_metadata",
        "Build integrations with any package managers you support",
        "Provide PackageMetadataInfo directly on your rules' targets",
        "Users shouldn't need overrides for the common path",
    ]),
    (right_col, "If you are an end user", [
        "Depend on @package_metadata and @supply_chain_tools",
        "Add spdx and cyclonedx targets to your release rules",
        "Layer package_metadata_override where a dep needs adjusting",
        "Wire in validation actions where you need enforcement",
    ]),
]:
    # Header card
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                            Emu(left), Emu(col_top), Emu(col_w), Emu(500000))
    sh.fill.solid()
    sh.fill.fore_color.rgb = NODE_FILL
    sh.line.color.rgb = BRIGHT_GREEN
    sh.line.width = Pt(1.5)
    tf = sh.text_frame; tf.word_wrap = True
    tf.margin_left = Emu(120000); tf.margin_right = Emu(120000)
    tf.margin_top = Emu(80000); tf.margin_bottom = Emu(80000)
    clear_tf(tf)
    add_paragraph(tf, header, size=18, bold=True, color=WHITE,
                  bullet=False, align=PP_ALIGN.CENTER, first=True)
    # Bullet list
    add_bullets_textbox(s, left, col_top + 550000, col_w, col_h - 550000,
                        [(b, 0) for b in bullets],
                        base_size=15, color=WHITE)


# ---------- Slide 16: Roadmap: coverage & ruleset integration ----------
s = prs.slides.add_slide(L_BODY)
add_title(s, "Roadmap: coverage and ruleset integration")
add_body_bullets(s, [
    ("Land package_metadata in core rulesets", 0),
    ("rules_cc, rules_java, rules_python, and bazel-contrib projects", 1),
    ("BCR validation so modules ship metadata by default", 0),
    ("Goal: no dependency untracked unless explicitly opted out", 0),
    ("Push accountability from the target graph down to individual actions", 0),
], base_size=17)


# ---------- Slide 17: Roadmap: deeper ecosystem coverage ----------
s = prs.slides.add_slide(L_BODY)
add_title(s, "Roadmap: deeper ecosystem coverage")
add_body_bullets(s, [
    ("Rules, module extensions, and macro definitions as first-class supply-chain nodes", 0),
    ("The graph today ends at target boundaries. We're pushing past that", 1),
    ("Bzlmod and lockfile provenance", 0),
    ("Toolchain and exec-platform attestation", 0),
    ("Know not just what you built, but who and what built it", 1),
], base_size=17)


# ---------- Slide 18: Roadmap: strict enforcement & attestation ----------
s = prs.slides.add_slide(L_BODY)
add_title(s, "Roadmap: strict enforcement and attestation")
add_body_bullets(s, [
    ("SBOM signing and verification", 0),
    ("Secure provenance emission", 0),
    ("Action-cache signing integration", 0),
    ("End-to-end artifact attestation. Origin and composition", 0),
    ("The path from advisory metadata to hermetic, verifiable policy", 0),
], base_size=18)


# ---------- Slide 19: What we need from you ----------
s = prs.slides.add_slide(L_TITLE_ONLY)
add_title(s, "What we need from you")
add_bullets_textbox(s, 311700, 1000000, 6400000, 3700000, [
    ("Try 1.0 on a real project and file issues", 0),
    ("1.0 stabilises the API, but the surrounding ecosystem is still moving", 1),
    ("Contribute ecosystem overlays", 0),
    ("JVM, Go, Python, JS, Rust. Pick your language and start", 1),
    ("Join our Birds-of-a-Feather session", 0),
    ("Supply-Chain BoF, Thursday 14:45, Room 11-14", 1),
    ("An open forum for ruleset maintainers, security engineers, compliance teams", 1),
], base_size=15, color=WHITE)
add_qr_with_label(s, QR_BOF,
                  left=7100000, top=1300000, size=1700000,
                  label="Supply-Chain BoF\nThu 14:45 · Room 11-14",
                  label_size=11, label_width=1900000)


# ---------- Slide 20: Resources ----------
s = prs.slides.add_slide(L_TITLE_ONLY)
add_title(s, "Resources")

# Three QR tiles across the top
tile_size = 1700000
tile_top = 1050000
gap = 800000
total_w = 3 * tile_size + 2 * gap
start_left = (9144000 - total_w) // 2

tiles = [
    (QR_REPO,   "Repo\nbazel-contrib/supply-chain"),
    (QR_BOF,    "Supply-Chain BoF\nThu 14:45 · Room 11-14"),
    (QR_VALACT, "Validation actions\nbazel.build docs"),
]
for i, (qr, label) in enumerate(tiles):
    left = start_left + i * (tile_size + gap)
    add_qr_with_label(s, qr, left=left, top=tile_top, size=tile_size,
                      label=label, label_size=11, label_width=tile_size + 400000)

# Bottom block: SIG roster + Slack + meeting time (text only)
tb = s.shapes.add_textbox(Emu(311700), Emu(3550000), Emu(8520600), Emu(1300000))
tb.fill.background(); tb.line.fill.background()
tf = tb.text_frame; tf.word_wrap = True
clear_tf(tf)
add_paragraph(tf, "Slack: #supply-chain-security on bazelbuild",
              size=15, color=WHITE, bullet=False,
              align=PP_ALIGN.CENTER, first=True)
add_paragraph(tf, "Weekly meeting: Thursdays 8:30 EST / 14:30 CET",
              size=15, color=WHITE, bullet=False, align=PP_ALIGN.CENTER)
add_paragraph(tf, "", size=6, bullet=False)
add_paragraph(tf,
              "Supply-Chain SIG: Florian (fweikert), Kaloyan (kraev-at-bc), "
              "Mark (mzeren-vmw), Simon (shs96c), Tony (aiuto)",
              size=14, color=WHITE, bullet=False,
              align=PP_ALIGN.CENTER)


# ---------- Slide 21: Q&A ----------
s = prs.slides.add_slide(L_SECTION)
for ph in s.placeholders:
    if ph.placeholder_format.idx == 0:
        tf = ph.text_frame
        clear_tf(tf)
        add_paragraph(tf, "Q&A", size=88, bold=True, color=WHITE,
                      bullet=False, align=PP_ALIGN.CENTER, first=True)


prs.save(OUTPUT)
print(f"Wrote {OUTPUT}")
print(f"Slide count: {len(prs.slides)}")
