import re

from domdown.utils.dom import is_dangerous_url


def bbcode_to_html(bbcode: str) -> str:
    html = bbcode

    html = re.sub(r"\[h1\]([\s\S]*?)\[/h1\]", r"<h1>\1</h1>", html, flags=re.IGNORECASE)
    html = re.sub(r"\[h2\]([\s\S]*?)\[/h2\]", r"<h2>\1</h2>", html, flags=re.IGNORECASE)
    html = re.sub(r"\[h3\]([\s\S]*?)\[/h3\]", r"<h3>\1</h3>", html, flags=re.IGNORECASE)

    html = re.sub(r"\[b\]([\s\S]*?)\[/b\]", r"<strong>\1</strong>", html, flags=re.IGNORECASE)
    html = re.sub(r"\[i\]([\s\S]*?)\[/i\]", r"<em>\1</em>", html, flags=re.IGNORECASE)
    html = re.sub(r"\[u\]([\s\S]*?)\[/u\]", r"<u>\1</u>", html, flags=re.IGNORECASE)
    html = re.sub(r"\[s\]([\s\S]*?)\[/s\]", r"<s>\1</s>", html, flags=re.IGNORECASE)

    def replace_url(match: re.Match) -> str:
        href = match.group(1)
        text = match.group(2)
        if is_dangerous_url(href):
            return text
        return f'<a href="{href}">{text}</a>'

    html = re.sub(
        r'\[url=["\']?([^"\'\]]+)["\']?\]([\s\S]*?)\[/url\]',
        replace_url,
        html,
        flags=re.IGNORECASE,
    )

    html = re.sub(r"\[img\]([\s\S]*?)\[/img\]", r'<img src="\1">', html, flags=re.IGNORECASE)

    html = re.sub(
        r'\[previewyoutube=["\']?([^;\'"]+)[^"\']*\][\s\S]*?\[/previewyoutube\]',
        r'<img src="https://www.youtube.com/watch?v=\1">',
        html,
        flags=re.IGNORECASE,
    )

    def replace_list(inner: str) -> str:
        items = re.sub(r"\[\*\]([\s\S]*?)(?=\[\*\]|\[\/list\]|$)", r"<li>\1</li>", inner, flags=re.IGNORECASE)
        return f"<ul>{items}</ul>"

    html = re.sub(r"\[list\]([\s\S]*?)\[/list\]", lambda m: replace_list(m.group(1)), html, flags=re.IGNORECASE)

    def replace_olist(inner: str) -> str:
        items = re.sub(r"\[\*\]([\s\S]*?)(?=\[\*\]|\[\/olist\]|$)", r"<li>\1</li>", inner, flags=re.IGNORECASE)
        return f"<ol>{items}</ol>"

    html = re.sub(r"\[olist\]([\s\S]*?)\[/olist\]", lambda m: replace_olist(m.group(1)), html, flags=re.IGNORECASE)

    html = re.sub(
        r"\[quote(?:=[^\]]+)?\]([\s\S]*?)\[/quote\]", r"<blockquote>\1</blockquote>", html, flags=re.IGNORECASE
    )

    html = re.sub(r"\[code\]([\s\S]*?)\[/code\]", r"<pre><code>\1</code></pre>", html, flags=re.IGNORECASE)

    html = re.sub(
        r"\[spoiler\]([\s\S]*?)\[/spoiler\]",
        r"<details><summary>Spoiler</summary>\1</details>",
        html,
        flags=re.IGNORECASE,
    )

    def replace_p(match: re.Match) -> str:
        inner = match.group(1).replace("\n", "<br>")
        return f"<p>{inner}</p>"

    html = re.sub(r"\[p\]([\s\S]*?)\[/p\]", replace_p, html, flags=re.IGNORECASE)

    html = html.replace("\n", "<br>")

    html = re.sub(r"\[[^\]]+\]", "", html)

    return html
