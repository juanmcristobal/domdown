from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

from domdown.fetch import BOT_UA, clean_markdown_content, extract_raw_markdown, fetch_page, get_initial_ua
from domdown.node import parse as domdown_parse
from domdown.utils import count_words

try:
    from importlib.metadata import version as get_version

    _VERSION = get_version("domdown")
except Exception:
    _VERSION = "0.0.0"

_USE_COLOR = sys.stdout.isatty() if hasattr(sys.stdout, "isatty") else False


def _red(s: str) -> str:
    return f"\033[31m{s}\033[39m" if _USE_COLOR else s


def _green(s: str) -> str:
    return f"\033[32m{s}\033[39m" if _USE_COLOR else s


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="domdown",
        description="Extract article content from web pages",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {_VERSION}")

    subparsers = parser.add_subparsers(dest="command")

    parse_cmd = subparsers.add_parser("parse", help="Parse HTML content from a file or URL")
    parse_cmd.add_argument("source", help="HTML file path or URL to parse")
    parse_cmd.add_argument("-o", "--output", help="Output file path (default: stdout)")
    parse_cmd.add_argument("-m", "--markdown", action="store_true", help="Convert content to markdown format")
    parse_cmd.add_argument("--md", action="store_true", help="Alias for --markdown")
    parse_cmd.add_argument(
        "-j", "--json", action="store_true", dest="json_output", help="Output as JSON with metadata and content"
    )
    parse_cmd.add_argument(
        "-t", "--plain-text", action="store_true", dest="plain_text", help="Output plain text (strip HTML tags)"
    )
    parse_cmd.add_argument("-p", "--property", help="Extract a specific property (e.g., title, description, domain)")
    parse_cmd.add_argument("--debug", action="store_true", help="Enable debug mode")
    parse_cmd.add_argument("-l", "--lang", help="Preferred language (BCP 47, e.g. en, fr, ja)")

    return parser


def _run(source: str, options: argparse.Namespace) -> None:
    use_markdown = options.markdown or options.md

    from .types import DomdownOptions

    opts = DomdownOptions(
        debug=options.debug,
        markdown=use_markdown,
        separate_markdown=use_markdown or options.json_output,
        language=options.lang,
    )

    is_url = source.startswith("http://") or source.startswith("https://")

    html: str
    url: Optional[str] = None

    if is_url:
        url = source
        initial_ua = get_initial_ua(source)
        html = fetch_page(source, initial_ua, options.lang)
    else:
        file_path = Path(source).resolve()
        html = file_path.read_text(encoding="utf-8")

    result = domdown_parse(html, url or "", opts)

    if is_url and result.word_count == 0:
        try:
            bot_html = fetch_page(source, BOT_UA, options.lang)

            raw_md = extract_raw_markdown(bot_html)
            if raw_md:
                bot_result = domdown_parse(bot_html, url or "", opts)
                bot_result.content = clean_markdown_content(raw_md)
                bot_result.word_count = count_words(bot_result.content)
                result = bot_result
            else:
                bot_result = domdown_parse(bot_html, url or "", opts)
                if bot_result.word_count > 0:
                    result = bot_result
        except Exception:
            pass

    text_content = re.sub(r"<[^>]*>", "", result.content).strip()
    if not text_content:
        print(_red(f"Error: No content could be extracted from {source}"), file=sys.stderr)
        sys.exit(1)

    output: str

    if options.property:
        prop = options.property
        val = getattr(result, prop, None)
        if val is not None:
            output = str(val)
        else:
            print(_red(f'Error: Property "{prop}" not found in response'), file=sys.stderr)
            sys.exit(1)
    elif options.json_output:
        data = {
            "content": result.content,
            "title": result.title,
            "description": result.description,
            "domain": result.domain,
            "favicon": result.favicon,
            "image": result.image,
            "language": result.language,
            "metaTags": [
                {"name": t.name, "property": t.property, "content": t.content} for t in (result.meta_tags or [])
            ],
            "parseTime": result.parse_time,
            "published": result.published,
            "author": result.author,
            "site": result.site,
            "schemaOrgData": result.schema_org_data,
            "wordCount": result.word_count,
        }
        if result.content_markdown:
            data["contentMarkdown"] = result.content_markdown
        if result.variables:
            data["variables"] = result.variables
        output = json.dumps(data, indent=2, ensure_ascii=False)
    elif options.plain_text:
        output = re.sub(r"<[^>]*>", "", result.content).strip()
    else:
        output = result.content

    if options.output:
        out_path = Path(options.output).resolve()
        out_path.write_text(output, encoding="utf-8")
        print(_green(f"Output written to {options.output}"))
    else:
        print(output)


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "parse":
        try:
            _run(args.source, args)
        except Exception as error:
            print(_red("Error:"), str(error), file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
