import re
import html

def split_ai_response_message(markdown_message: str) -> list[str]:
    telegram_char_limit = 4096
    code_fence = "```"

    messages: list[str] = []
    current_lines: list[str] = []
    current_len = 0
    in_code_block = False
    code_block_lang = ""

    for line in markdown_message.split("\n"):
        stripped = line.strip()

        # Detect code fence
        if stripped.startswith(code_fence):
            if not in_code_block:
                code_block_lang = stripped[len(code_fence):]
                in_code_block = True
            else:
                in_code_block = False
                code_block_lang = ""

        line_len = len(line) + 1  # newline

        # If adding line exceeds limit, flush
        if current_len + line_len > telegram_char_limit:
            if in_code_block:
                # Close code block before flushing
                current_lines.append(code_fence)
                messages.append("\n".join(current_lines))
                current_lines = [f"{code_fence}{code_block_lang}"]
                current_len = len(current_lines[0]) + 1
            else:
                messages.append("\n".join(current_lines))
                current_lines = []
                current_len = 0

        current_lines.append(line)
        current_len += line_len

    # Final flush
    if current_lines:
        messages.append("\n".join(current_lines))

    return messages


def markdown_to_telegram_html(text):
    # Escape everything first
    text = html.escape(text)

    # Tables → <pre>
    table_re = re.compile(
        r'(\|.+\|\n\|[-:\s|]+\|\n(?:\|.*\|\n?)*)'
    )
    text = table_re.sub(lambda m: f"<pre>{m.group(1)}</pre>", text)

    # Headers
    text = re.sub(r'^#{1,6}\s+(.+)$', r'<b>\1</b>', text, flags=re.MULTILINE)

    # Links: [text](url)
    text = re.sub(
        r'\[([^\]]+)\]\((https?://[^\s)]+)\)',
        r'<a href="\2">\1</a>',
        text
    )

    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)

    # Italic
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)

    return text
