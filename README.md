# Formatador App

App em Python + Flask para formatar listas, palavras, links e blocos de texto.

## Recursos

- Interface clean com Bootstrap 5
- Porta fixa `5442`
- Formatações gerais para Markdown/Obsidian
- Dashboard diário pronto
- Formatações específicas para Telegram
- Formatações específicas para WhatsApp
- Exportação em `.md` ou `.txt`
- Preview simples do resultado

## Como rodar

### Windows

Use o `run.bat` ou `run.ps1`.

### Manual

```bash
pip install -r requirements.txt
python app.py
```

Abra no navegador:

```text
http://127.0.0.1:5442
```

## Novas ações

- Pular uma linha entre itens
- Criar um bloco de código Markdown para cada item da lista


## Python List Maker

Nova ação:

- `Python list: deixar em pé`

Exemplo:

```python
py_list = ['Projeto A', 'Projeto B']
```

vira:

```python
py_list = [
    'Projeto A',
    'Projeto B'
]
```

## Snippets adicionados

- Python CLI com argparse
- Python Flask API
- Python ler/salvar TXT
- BAT para rodar app Python
- BAT para abrir 4 terminais
- PowerShell runner
- Git add/commit/push
- requirements.txt básico


## Jsonificar serviços

Nova ação em Snippets:

- `Jsonificar serviços`

Converte blocos como:

```text
SERVICE_NAME:"Favoritos_app",
STATUS:"Activated",
ROOT_DIR:"C:\xampp\htdocs\favoritos_app",
```

em JSON válido com a chave raiz `services`.


## Favoritos e múltiplas ações

Adicionado:

- Ações favoritas com `localStorage`
- Múltiplas ações em sequência
- Múltiplas ações favoritas
- Campo `Adicionar antes`
- `run.bat` com `mode con: cols=68 lines=14`


## Ações especiais avançadas

Adicionado no card `Ações especiais`:

- Adicionar antes
- Adicionar após
- Adicionar entre
- Trocar
- Repetir entrada
- Blank lines antes/depois
- Preservar blank spaces antes/depois
