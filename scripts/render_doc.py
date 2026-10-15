"""Render a Jinja2 markdown template with the numbers dictionary, then convert to .docx with pandoc.

Numbers come from output/tables/paper_numbers.json (written by the paper script),
so no estimate is ever typed by hand. Jinja comment delimiters are changed to
<#-- --#> because pandoc uses {#refs} for the reference list.

Usage:
  python render_doc.py <template.md> <out.md> [--numbers output/tables/paper_numbers.json]
                       [--bib paper/references.bib] [--toc] [--resource-path dir1:dir2]

In templates: {{ n.rq1_h12 }} for a number; put `::: {#refs}` / `:::` where the
reference list goes; escape a literal @ as \@; leave blank lines around tables.
"""

import argparse
import json
from pathlib import Path

import jinja2
import pypandoc


def render(template, out, numbers=None, bib=None, toc=False, resource_path=None, tables=None):
    template, out = Path(template), Path(out)
    n = json.loads(Path(numbers).read_text()) if numbers else {}
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template.parent), undefined=jinja2.StrictUndefined,
                             keep_trailing_newline=True, comment_start_string="<#--", comment_end_string="--#>")
    text = env.get_template(template.name).render(n=n, t=tables or {})
    out.write_text(text)
    args = []
    if bib:
        args += ["--citeproc", f"--bibliography={bib}", "--metadata=link-citations:true"]
    if toc:
        args += ["--toc", "--toc-depth=2"]
    args.append(f"--resource-path={resource_path or out.parent}")
    pypandoc.convert_file(str(out), "docx", outputfile=str(out.with_suffix(".docx")), extra_args=args)
    print("wrote", out, "and", out.with_suffix(".docx"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("template")
    ap.add_argument("out")
    ap.add_argument("--numbers")
    ap.add_argument("--bib")
    ap.add_argument("--toc", action="store_true")
    ap.add_argument("--resource-path")
    a = ap.parse_args()
    render(a.template, a.out, a.numbers, a.bib, a.toc, a.resource_path)
