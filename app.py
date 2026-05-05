from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Callable

from flask import Flask, jsonify, render_template, request, send_file

BASE_DIR = Path(__file__).resolve().parent
EXPORT_DIR = BASE_DIR / "exports"
EXPORT_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False


def clean_lines(text: str) -> list[str]:
    return [line.strip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]


def non_empty_lines(text: str) -> list[str]:
    return [line for line in clean_lines(text) if line]


def remove_blank_lines(text: str) -> str:
    return "\n".join(non_empty_lines(text))


def unique_lines(text: str) -> str:
    seen: set[str] = set()
    out: list[str] = []
    for line in clean_lines(text):
        if not line:
            continue
        key = line.lower()
        if key not in seen:
            seen.add(key)
            out.append(line)
    return "\n".join(out)


def bullet_list(text: str) -> str:
    return "\n".join(f"- {line}" for line in non_empty_lines(text))


def checkbox_list(text: str) -> str:
    return "\n".join(f"- [ ] {line}" for line in non_empty_lines(text))


def numbered_list(text: str) -> str:
    return "\n".join(f"{idx}. {line}" for idx, line in enumerate(non_empty_lines(text), start=1))


def quote_block(text: str) -> str:
    return "\n".join(f"> {line}" if line else ">" for line in clean_lines(text))


def comma_list(text: str) -> str:
    return ", ".join(non_empty_lines(text))


def pipe_list(text: str) -> str:
    return " | ".join(non_empty_lines(text))


def lowercase(text: str) -> str:
    return text.lower()


def uppercase(text: str) -> str:
    return text.upper()


def titlecase(text: str) -> str:
    return "\n".join(line.title() for line in clean_lines(text))


def slugify(text: str) -> str:
    output = []
    for line in clean_lines(text):
        if not line:
            continue
        item = line.lower()
        item = re.sub(r"[^a-z0-9à-ÿ]+", "-", item, flags=re.IGNORECASE)
        item = re.sub(r"-+", "-", item).strip("-")
        output.append(item)
    return "\n".join(output)


def obsidian_links(text: str) -> str:
    return "\n".join(f"[[{line}]]" for line in non_empty_lines(text))


def markdown_table(text: str) -> str:
    lines = non_empty_lines(text)
    if not lines:
        return ""

    rows: list[list[str]] = []
    for line in lines:
        if "|" in line:
            row = [cell.strip() for cell in line.strip("|").split("|")]
        elif ";" in line:
            row = [cell.strip() for cell in line.split(";")]
        elif "," in line:
            row = [cell.strip() for cell in line.split(",")]
        else:
            row = [line]
        rows.append(row)

    max_cols = max(len(row) for row in rows)
    rows = [row + [""] * (max_cols - len(row)) for row in rows]
    header = rows[0]
    body = rows[1:] if len(rows) > 1 else []

    table = ["| " + " | ".join(header) + " |", "| " + " | ".join(["---"] * max_cols) + " |"]
    table += ["| " + " | ".join(row) + " |" for row in body]
    return "\n".join(table)


def code_block(text: str, language: str = "") -> str:
    return f"```{language}\n{text.strip()}\n```" if text.strip() else ""


def extract_links(text: str) -> str:
    links = re.findall(r"https?://[^\s\])}>\"']+", text)
    seen: set[str] = set()
    out: list[str] = []
    for link in links:
        if link not in seen:
            seen.add(link)
            out.append(link)
    return "\n".join(out)




def blank_line_between_items(text: str) -> str:
    """Coloca uma linha em branco entre cada item não vazio."""
    return "\n\n".join(non_empty_lines(text))


def code_block_each_item(text: str) -> str:
    """Cria um bloco de código Markdown para cada item não vazio."""
    return "\n\n".join(f"```\n{line}\n```" for line in non_empty_lines(text))




def python_list_vertical(text: str) -> str:
    """
    Transforma uma lista Python "deitada" em lista "em pé".

    Exemplo:
    py_list = ['Projeto A', 'Projeto B']

    Vira:
    py_list = [
        'Projeto A',
        'Projeto B'
    ]
    """
    raw = text.strip()
    if not raw:
        return ""

    match = re.search(r"^(?P<prefix>\s*[A-Za-z_][A-Za-z0-9_]*\s*=\s*)\[(?P<body>.*)\]\s*$", raw, flags=re.S)
    if match:
        prefix = match.group("prefix").strip()
        body = match.group("body")
    else:
        prefix = "py_list ="
        if raw.startswith("[") and raw.endswith("]"):
            body = raw[1:-1]
        else:
            body = raw

    items = []
    current = []
    quote = None
    escaped = False
    bracket_depth = 0

    for char in body:
        if escaped:
            current.append(char)
            escaped = False
            continue

        if char == "\\":
            current.append(char)
            escaped = True
            continue

        if quote:
            current.append(char)
            if char == quote:
                quote = None
            continue

        if char in ("'", '"'):
            quote = char
            current.append(char)
            continue

        if char in "([{":
            bracket_depth += 1
            current.append(char)
            continue

        if char in ")]}":
            bracket_depth = max(0, bracket_depth - 1)
            current.append(char)
            continue

        if char == "," and bracket_depth == 0:
            item = "".join(current).strip()
            if item:
                items.append(item)
            current = []
            continue

        current.append(char)

    last = "".join(current).strip()
    if last:
        items.append(last)

    if not items:
        return f"{prefix} []"

    lines = [f"{prefix} ["]
    for index, item in enumerate(items):
        comma = "," if index < len(items) - 1 else ""
        lines.append(f"    {item}{comma}")
    lines.append("]")
    return "\n".join(lines)


def snippet_python_cli() -> str:
    return """import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Meu script Python")
    parser.add_argument("-i", "--input", required=True, help="Arquivo ou pasta de entrada")
    parser.add_argument("-o", "--output", required=True, help="Pasta de saída")
    parser.add_argument("--dry-run", action="store_true", help="Simula sem alterar nada")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Entrada: {input_path}")
    print(f"Saída: {output_path}")
    print(f"Dry-run: {args.dry_run}")


if __name__ == "__main__":
    main()
"""


def snippet_python_flask() -> str:
    return """from flask import Flask, jsonify, render_template, request

app = Flask(__name__)





@app.route("/")
def index():
    return render_template("index.html")


@app.post("/api/processar")
def processar():
    payload = request.get_json(silent=True) or {}
    texto = payload.get("texto", "")
    return jsonify({"ok": True, "resultado": texto.upper()})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5442, debug=True)
"""


def snippet_python_read_write() -> str:
    return """from pathlib import Path

entrada = Path(r"C:\\caminho\\entrada.txt")
saida = Path(r"C:\\caminho\\saida.txt")

texto = entrada.read_text(encoding="utf-8")
linhas = [linha.strip() for linha in texto.splitlines() if linha.strip()]

saida.write_text("\\n".join(linhas) + "\\n", encoding="utf-8")

print(f"Arquivo salvo em: {saida}")
"""


def snippet_bat_runner() -> str:
    return """@echo off
title Rodar App Python
cd /d "%~dp0"

echo Instalando dependencias...
python -m pip install -r requirements.txt

echo.
echo Iniciando app...
python app.py

pause
"""


def snippet_bat_four_terminals() -> str:
    return """@echo off
REM Abre quatro terminais na pasta atual
cd /d "%~dp0"

wt ^
  new-tab --title "Terminal 1" cmd /k "cd /d %cd%" ^
; new-tab --title "Terminal 2" cmd /k "cd /d %cd%" ^
; new-tab --title "Terminal 3" cmd /k "cd /d %cd%" ^
; new-tab --title "Terminal 4" cmd /k "cd /d %cd%"
"""


def snippet_powershell_runner() -> str:
    return """Set-Location $PSScriptRoot

Write-Host "Instalando dependencias..." -ForegroundColor Cyan
python -m pip install -r requirements.txt

Write-Host "Iniciando app..." -ForegroundColor Green
python app.py
"""


def snippet_git_basic() -> str:
    return """git status
git add .
git commit -m "Atualiza projeto"
git branch -M main
git push -u origin main
"""


def snippet_requirements() -> str:
    return """Flask==3.0.3
requests==2.32.3
python-dotenv==1.0.1
rich==13.9.4
"""




def jsonificar_services(text: str) -> str:
    """
    Converte blocos estilo KEY:"VALUE", em JSON no formato:
    {"services": [{...}, {...}]}
    """
    services: list[dict[str, str]] = []
    current: dict[str, str] = {}

    pattern = re.compile(
        r"^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?P<value>.*?)(?:,\s*)?$"
    )

    for raw_line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        line = raw_line.strip()

        if not line:
            if current:
                services.append(current)
                current = {}
            continue

        match = pattern.match(line)
        if not match:
            continue

        key = match.group("key").strip()
        value = match.group("value").strip().rstrip(",").strip()

        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]

        if key == "SERVICE_NAME" and current:
            services.append(current)
            current = {}

        current[key] = value

    if current:
        services.append(current)

    return json.dumps({"services": services}, ensure_ascii=False, indent=2)


# =========================
# Formatações para Telegram
# =========================

def telegram_bullets(text: str) -> str:
    return "\n".join(f"• {line}" for line in non_empty_lines(text))


def telegram_numbered(text: str) -> str:
    return "\n".join(f"{idx}) {line}" for idx, line in enumerate(non_empty_lines(text), start=1))


def telegram_quote(text: str) -> str:
    return "\n".join(f"> {line}" for line in non_empty_lines(text))


def telegram_spoiler(text: str) -> str:
    return "\n".join(f"||{line}||" for line in non_empty_lines(text))


def telegram_bold_lines(text: str) -> str:
    return "\n".join(f"**{line}**" for line in non_empty_lines(text))


# =========================
# Formatações para WhatsApp
# =========================

def whatsapp_bullets(text: str) -> str:
    return "\n".join(f"• {line}" for line in non_empty_lines(text))


def whatsapp_checklist(text: str) -> str:
    return "\n".join(f"☐ {line}" for line in non_empty_lines(text))


def whatsapp_bold_lines(text: str) -> str:
    return "\n".join(f"*{line}*" for line in non_empty_lines(text))


def whatsapp_italic_lines(text: str) -> str:
    return "\n".join(f"_{line}_" for line in non_empty_lines(text))


def whatsapp_strike_lines(text: str) -> str:
    return "\n".join(f"~{line}~" for line in non_empty_lines(text))


def dashboard_template() -> str:
    today = datetime.now().strftime("%d/%m/%Y")
    return f"""# 🚀 Dashboard Diário — {today}

## 🎯 Foco do dia

> [!TIP]  
> Escreva aqui o que REALMENTE importa hoje.

---

## ✅ Tarefas

- [ ] Tarefa 1
- [ ] Tarefa 2
- [ ] Tarefa 3

---

## ⚡ Em andamento

- [/] Algo que você já começou

---

## 🧠 Ideias rápidas

> [!NOTE]  
> Joga tudo aqui sem filtro.

---

## 📦 Projetos ativos

- [[Projeto A]]
- [[Projeto B]]

---

## 📊 Progresso do dia

Progresso: ████░░░░░░ 40%

---

## 🧪 Snippets / comandos úteis

> [!TIP]  
> Coisas que você usa sempre.

```bash
yt-dlp -vU --cookies cookies.txt
```

```python
print("testando")
```

---

## 📅 Agenda

- ⏰ 09:00 -
- ⏰ 14:00 -
- ⏰ 18:00 -

---

## 🔍 Detalhes

<details>
<summary>Mostrar detalhes</summary>

- Pensamentos soltos
- Coisas pra revisar depois
- Links úteis

</details>

---

## 🧱 Log do dia

- 🟢 Comecei o dia com...
- 🟡 Tive dificuldade em...
- 🔴 Preciso melhorar...

---

## 🧭 Próximo passo

> [!WARNING]  
> Se você fizer só UMA coisa depois disso, que seja:
"""


def _split_input_lines(text: str, preserve_spaces: bool = False) -> list[str]:
    """Divide linhas mantendo espaços quando preserve_spaces=True."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if preserve_spaces:
        return lines
    return [line.strip() for line in lines]


def _apply_blank_lines(text: str, before_enabled: bool = False, after_enabled: bool = False, before_count: int = 3, after_count: int = 3) -> str:
    """Adiciona linhas em branco antes/depois do resultado final."""
    output = text
    if before_enabled:
        output = ("\n" * max(1, before_count)) + output
    if after_enabled:
        output = output + ("\n" * max(1, after_count))
    return output


def add_before_each_item(text: str, prefix: str = "", preserve_spaces: bool = False, **kwargs) -> str:
    """Insere um texto antes de cada linha/item não vazio."""
    prefix = (prefix or "").strip()
    if not prefix:
        return text
    output: list[str] = []
    for line in _split_input_lines(text, preserve_spaces=preserve_spaces):
        if line.strip():
            output.append(f"{prefix} {line}")
        else:
            output.append("")
    return "\n".join(output).strip("\n")


def add_after_each_item(text: str, suffix: str = "", preserve_spaces: bool = False, **kwargs) -> str:
    """Insere um texto após cada linha/item não vazio."""
    suffix = (suffix or "").strip()
    if not suffix:
        return text
    output: list[str] = []
    for line in _split_input_lines(text, preserve_spaces=preserve_spaces):
        if line.strip():
            output.append(f"{line} {suffix}")
        else:
            output.append("")
    return "\n".join(output).strip("\n")


def add_between_words(text: str, separator: str = "", preserve_spaces: bool = False, **kwargs) -> str:
    """Insere um texto entre palavras."""
    if separator == "":
        return text
    output: list[str] = []
    for line in _split_input_lines(text, preserve_spaces=preserve_spaces):
        if not line.strip():
            output.append(line if preserve_spaces else "")
            continue
        words = line.split()
        output.append(separator.join(words))
    return "\n".join(output).strip("\n")


def replace_text_content(text: str, old: str = "", new: str = "", **kwargs) -> str:
    """Troca um conteúdo por outro, estilo Ctrl+F / Ctrl+H."""
    if old == "":
        return text
    return text.replace(old, new)


def repeat_input_text(text: str, count: int = 1, preserve_spaces: bool = False, **kwargs) -> str:
    """Repete a entrada a quantidade informada."""
    try:
        count = int(count)
    except (TypeError, ValueError):
        count = 1
    count = max(1, min(count, 10000))
    content = text if preserve_spaces else text.strip()
    return "\n".join(content for _ in range(count))


def apply_special_action(text: str, action: str, options: dict) -> str:
    """Aplica ações especiais que dependem dos campos do card Ações especiais."""
    preserve_spaces = bool(options.get("preserve_spaces", False))
    if action == "add_before":
        return add_before_each_item(text, options.get("add_before", ""), preserve_spaces=preserve_spaces)
    if action == "add_after":
        return add_after_each_item(text, options.get("add_after", ""), preserve_spaces=preserve_spaces)
    if action == "add_between":
        return add_between_words(text, options.get("add_between", ""), preserve_spaces=preserve_spaces)
    if action == "replace_text":
        return replace_text_content(text, options.get("replace_from", ""), options.get("replace_to", ""))
    if action == "repeat_input":
        return repeat_input_text(text, options.get("repeat_count", 1), preserve_spaces=preserve_spaces)
    return text


def apply_formatter_pipeline(text: str, actions: list[str], options: dict | None = None) -> str:
    """Aplica múltiplas ações na ordem recebida."""
    options = options or {}
    output = text
    special_actions = {"add_before", "add_after", "add_between", "replace_text", "repeat_input"}
    for action in actions:
        if action in special_actions:
            output = apply_special_action(output, action, options)
            continue
        formatter = FORMATTERS.get(action)
        if formatter:
            output = formatter(output)
    return output

FORMATTERS: dict[str, Callable[[str], str]] = {
    "clean": remove_blank_lines,
    "unique": unique_lines,
    "bullets": bullet_list,
    "checkbox": checkbox_list,
    "numbered": numbered_list,
    "quote": quote_block,
    "comma": comma_list,
    "pipe": pipe_list,
    "lower": lowercase,
    "upper": uppercase,
    "title": titlecase,
    "slug": slugify,
    "obsidian": obsidian_links,
    "table": markdown_table,
    "code": lambda text: code_block(text),
    "bash": lambda text: code_block(text, "bash"),
    "python": lambda text: code_block(text, "python"),
    "links": extract_links,
    "blank_between": blank_line_between_items,
    "code_each": code_block_each_item,
    "telegram_bullets": telegram_bullets,
    "telegram_numbered": telegram_numbered,
    "telegram_quote": telegram_quote,
    "telegram_spoiler": telegram_spoiler,
    "telegram_bold": telegram_bold_lines,
    "whatsapp_bullets": whatsapp_bullets,
    "whatsapp_checklist": whatsapp_checklist,
    "whatsapp_bold": whatsapp_bold_lines,
    "whatsapp_italic": whatsapp_italic_lines,
    "whatsapp_strike": whatsapp_strike_lines,
    "python_list_vertical": python_list_vertical,
    "snippet_python_cli": lambda text: snippet_python_cli(),
    "snippet_python_flask": lambda text: snippet_python_flask(),
    "snippet_python_read_write": lambda text: snippet_python_read_write(),
    "snippet_bat_runner": lambda text: snippet_bat_runner(),
    "snippet_bat_four_terminals": lambda text: snippet_bat_four_terminals(),
    "snippet_powershell_runner": lambda text: snippet_powershell_runner(),
    "snippet_git_basic": lambda text: snippet_git_basic(),
    "snippet_requirements": lambda text: snippet_requirements(),
    "jsonificar_services": jsonificar_services,
    "dashboard": lambda text: dashboard_template(),
    "add_before": lambda text: add_before_each_item(text),
    "add_after": lambda text: add_after_each_item(text),
    "add_between": lambda text: add_between_words(text),
    "replace_text": lambda text: text,
    "repeat_input": lambda text: text,
}




def add_before_each_item(text: str, prefix: str = "", preserve_spaces: bool = False, **kwargs) -> str:
    """
    Insere um texto antes de cada linha/item não vazio.
    Exemplo: prefix="/fone" e linha "19999999999" -> "/fone 19999999999"
    """
    prefix = (prefix or "").strip()
    if not prefix:
        return text

    output: list[str] = []
    for line in _split_input_lines(text, preserve_spaces=preserve_spaces):
        if line.strip():
            output.append(f"{prefix} {line}")
        else:
            output.append("")
    return "\n".join(output).strip()


def apply_formatter_pipeline(text: str, actions: list[str], add_before: str = "") -> str:
    """
    Aplica múltiplas ações na ordem recebida.
    A ação especial add_before usa o campo "Adicionar antes".
    """
    output = text

    for action in actions:
        if action == "add_before":
            output = add_before_each_item(output, add_before)
            continue

        formatter = FORMATTERS.get(action)
        if formatter:
            output = formatter(output)

    return output


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/api/format")
def api_format():
    payload = request.get_json(silent=True) or {}
    text = payload.get("text", "")
    mode = payload.get("mode", "clean")
    actions = payload.get("actions") or []

    special_options = {
        "add_before": payload.get("add_before", ""),
        "add_after": payload.get("add_after", ""),
        "add_between": payload.get("add_between", ""),
        "replace_from": payload.get("replace_from", ""),
        "replace_to": payload.get("replace_to", ""),
        "repeat_count": payload.get("repeat_count", 1),
        "blank_lines_before": bool(payload.get("blank_lines_before", False)),
        "blank_lines_after": bool(payload.get("blank_lines_after", False)),
        "blank_lines_before_count": int(payload.get("blank_lines_before_count", 3) or 3),
        "blank_lines_after_count": int(payload.get("blank_lines_after_count", 3) or 3),
        "preserve_spaces": bool(payload.get("preserve_spaces", False)),
    }

    if isinstance(actions, list) and actions:
        output = apply_formatter_pipeline(text, actions, special_options)
    else:
        special_actions = {"add_before", "add_after", "add_between", "replace_text", "repeat_input"}
        if mode in special_actions:
            output = apply_special_action(text, mode, special_options)
        else:
            formatter = FORMATTERS.get(mode, remove_blank_lines)
            output = formatter(text)

    output = _apply_blank_lines(
        output,
        before_enabled=special_options["blank_lines_before"],
        after_enabled=special_options["blank_lines_after"],
        before_count=special_options["blank_lines_before_count"],
        after_count=special_options["blank_lines_after_count"],
    )

    return jsonify({"ok": True, "output": output, "mode": mode, "actions": actions})


@app.post("/api/export")
def api_export():
    payload = request.get_json(silent=True) or {}
    content = payload.get("content", "").strip()
    filename = payload.get("filename", "formatado.md").strip() or "formatado.md"
    filename = re.sub(r"[^\w\-. ]+", "_", filename)
    if not filename.lower().endswith((".md", ".txt")):
        filename += ".md"

    path = EXPORT_DIR / filename
    path.write_text(content + "\n", encoding="utf-8")
    return jsonify({"ok": True, "filename": filename, "download_url": f"/download/{filename}"})


@app.get("/download/<path:filename>")
def download(filename: str):
    safe_name = re.sub(r"[^\w\-. ]+", "_", filename)
    path = EXPORT_DIR / safe_name
    if not path.exists():
        return "Arquivo não encontrado", 404
    return send_file(path, as_attachment=True, download_name=safe_name)


@app.get("/health")
def health():
    return jsonify({"ok": True, "app": "Formatador de Listas", "port": 5442})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5442, debug=True)
