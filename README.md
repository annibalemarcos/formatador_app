# Formatador App

> **Status:** 🚧 Em desenvolvimento — este projeto ainda **não está pronto** para uso final/produção.  
> Ele já funciona para vários fluxos simples, mas ainda está em fase de testes, ajustes de interface e correção de bugs.

## 🧩 Sobre

O **Formatador App** é uma aplicação local feita com **Python + Flask + Bootstrap** para ajudar a formatar listas, textos, snippets e pequenos blocos de conteúdo rapidamente.

A ideia é jogar uma entrada meio bagunçada e sair com um resultado organizado, pronto para copiar, salvar ou reutilizar em ferramentas como Obsidian, Telegram, WhatsApp, scripts, arquivos `.md`, `.txt`, JSON etc.

É tipo uma bancada de oficina para texto: ainda tem parafuso no chão, mas a máquina já ronca.

---

## ⚠️ Aviso importante

Este projeto **ainda não está finalizado**.

Use com atenção, principalmente porque:

- algumas funções ainda estão sendo refinadas;
- a interface ainda pode mudar bastante;
- podem existir bugs em ações combinadas;
- algumas validações ainda são simples;
- o código ainda não passou por uma limpeza final;
- não é recomendado para produção.

---

## ✨ Funcionalidades atuais

### Formatações gerais

- Limpar linhas vazias
- Remover duplicadas
- Criar lista com bullets
- Criar checklist Markdown
- Criar lista numerada
- Criar bloco de citação
- Separar por vírgula
- Separar por pipe
- Converter para minúsculas
- Converter para maiúsculas
- Capitalizar título
- Gerar slug / URL amigável
- Criar links Obsidian `[[...]]`
- Criar tabela Markdown
- Criar bloco de código
- Extrair links únicos

### Listas e blocos

- Pular uma linha entre itens
- Criar bloco de código para cada item
- Transformar lista Python “deitada” em lista “em pé”

Exemplo:

```python
py_list = ['Projeto A', 'Projeto B', 'Comprar café']
```

vira:

```python
py_list = [
    'Projeto A',
    'Projeto B',
    'Comprar café'
]
```

### Ações especiais

- Adicionar texto antes de cada linha
- Adicionar texto após cada linha
- Adicionar texto entre palavras
- Trocar texto, estilo buscar/substituir
- Repetir entrada
- Opções para preservar espaços em branco
- Opções para adicionar linhas em branco antes/depois

### Múltiplas ações

O app permite montar uma sequência de ações e aplicar tudo em cadeia.

Exemplo de fluxo:

1. Adicionar antes `/fone`
2. Criar bloco de código por item

Entrada:

```text
19981747092
19983718133
19993676929
```

Resultado esperado:

````markdown
```
/fone 19981747092
```

```
/fone 19983718133
```

```
/fone 19993676929
```
````

### Favoritos

- Favoritar ações
- Remover ações favoritas
- Salvar sequências de múltiplas ações favoritas
- Reutilizar sequências salvas

> Os favoritos são salvos no navegador via `localStorage`.

### Snippets

O app também possui alguns snippets prontos, como:

- Python CLI com `argparse`
- Python Flask API
- Python ler/salvar `.txt`
- BAT para rodar app Python
- BAT para abrir terminais
- PowerShell runner
- Git básico
- `requirements.txt`

### Jsonificar serviços

Transforma blocos como:

```text
SERVICE_NAME:"Favoritos_app",
STATUS:"Activated",
ROOT_DIR:"C:\\xampp\\htdocs\\favoritos_app",
RUN_APP:"app.py",
```

em JSON válido:

```json
{
  "services": [
    {
      "SERVICE_NAME": "Favoritos_app",
      "STATUS": "Activated",
      "ROOT_DIR": "C:\\\\xampp\\\\htdocs\\\\favoritos_app",
      "RUN_APP": "app.py"
    }
  ]
}
```

---

## 🖼️ Interface

A interface usa:

- Bootstrap 5 via CDN
- Bootstrap Icons
- Layout claro e minimalista
- Cards com bordas arredondadas
- Acordeões para organizar ações
- Área de entrada
- Área de resultado
- Preview fiel preservando quebras de linha

---

## 🚀 Como rodar

### 1. Baixe ou clone o projeto

```bash
git clone https://github.com/SEU_USUARIO/formatador_app.git
cd formatador_app
```

### 2. Rode pelo `.bat` no Windows

```bat
run.bat
```

O `run.bat` cria o ambiente virtual, instala as dependências e abre o app no navegador.

### 3. Ou rode manualmente

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Depois acesse:

```text
http://127.0.0.1:5442
```

---

## 📦 Dependências

As dependências principais são:

```txt
Flask
```

Dependendo da versão do projeto, o `requirements.txt` pode conter versões fixas.

---

## 🗂️ Estrutura aproximada

```text
formatador_app/
├── app.py
├── requirements.txt
├── run.bat
├── run.ps1
├── README.md
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
└── templates/
    └── index.html
```

---

## 🛠️ Roadmap

Coisas que ainda precisam melhorar:

- [ ] Revisar toda a interface
- [ ] Corrigir bugs em ações combinadas
- [ ] Melhorar validações
- [ ] Criar testes automatizados
- [ ] Melhorar o sistema de favoritos
- [ ] Adicionar importação/exportação de favoritos
- [ ] Melhorar tratamento de JSON
- [ ] Separar melhor o código em módulos
- [ ] Criar documentação visual
- [ ] Preparar versão realmente estável

---

## 🧪 Estado atual

Este projeto está em fase de protótipo funcional.

Ele já é útil para uso local, mas ainda está mais para:

> “ferramenta pessoal em evolução”

Do que para:

> “produto final redondinho”.

---

## 🤝 Contribuições

Por enquanto, o projeto ainda está em construção e pode mudar bastante.

Mesmo assim, sugestões, ideias e melhorias são bem-vindas.

---

## 📄 Licença

Ainda não definida.

Se for publicar no GitHub, escolha uma licença antes de receber contribuições externas. Algumas opções comuns:

- MIT
- Apache 2.0
- GPLv3

---

## 👤 Autor

Projeto criado como ferramenta pessoal para acelerar formatação de textos, listas, snippets e pequenos blocos úteis do dia a dia.

---

## 🧠 Nota final

Este app nasceu de uma necessidade simples: parar de perder tempo formatando texto na mão.

Ainda está torto em alguns cantos? Sim.  
Mas já economiza clique, raiva e café. E isso, meu amigo, já é meio caminho para a civilização.
