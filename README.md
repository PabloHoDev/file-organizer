# 📁 Organizador de Arquivos em Python

Script em Python que organiza automaticamente os arquivos de uma pasta por tipo, estruturado
como um **pipeline ETL** e com relatório CSV de cada execução.

## 🗂️ Estrutura do projeto

```
file-organizer/
├── Organizador_Arquivo_Python/
│   └── main.py                  # pipeline ETL: extrair → transformar → carregar
├── scripts/
│   └── gerar_cenario_teste.py   # cria uma pasta bagunçada realista para teste manual
├── tests/
│   ├── test_colisao.py          # regressão da colisão de nomes (#2)
│   └── test_pipeline_etl.py     # testes de cada etapa do ETL
├── .github/workflows/ci.yml     # CI: format, lint, typecheck, testes e Gitleaks
├── pyproject.toml               # configuração de pytest, ruff e mypy
└── requirements-dev.txt         # ferramentas de desenvolvimento (versões fixas)
```

## 🔄 Pipeline ETL

```
 pasta bagunçada
       │
       ▼
┌─────────────┐   lista os arquivos da raiz e coleta metadados
│  EXTRACT    │   (nome, extensão normalizada, tamanho)
└─────────────┘   → list[ArquivoEncontrado]
       │
       ▼
┌─────────────┐   classifica por categoria e monta o plano de movimentação,
│  TRANSFORM  │   resolvendo colisões de nome. Não toca no disco.
└─────────────┘   → list[Movimento]
       │
       ▼
┌─────────────┐   executa o plano (um erro não interrompe os demais)
│    LOAD     │   e grava o relatório em _relatorios/organizacao_<data>.csv
└─────────────┘   → list[Resultado]
```

Separar as etapas deixa cada uma testável isoladamente e torna o *Transform* uma função pura:
dá para inspecionar o plano antes de mover qualquer arquivo. O relatório CSV (separador `;`,
UTF-8 com BOM) abre direto no Excel em português e serve de trilha de auditoria.

## 🚀 Funcionalidades
- Organização automática por tipo de arquivo
- Criação de pastas se não existirem
- Suporte a PDFs, imagens, planilhas, textos e arquivos compactados
- Nunca sobrescreve: se o destino já tem um arquivo com o mesmo nome, o novo vira `nome (1).ext`
- Relatório CSV de cada execução em `_relatorios/` (arquivo, tamanho, categoria, destino, status)
- Um erro em um arquivo não interrompe a organização dos demais

## 🧪 Como testar com um cenário pronto

O script `scripts/gerar_cenario_teste.py` cria uma pasta bagunçada que imita uma pasta de
Downloads real, incluindo casos de borda (extensão em maiúsculas, acentos, arquivos sem
extensão, extensões desconhecidas, subpastas e colisão de nome no destino).

```bash
python scripts/gerar_cenario_teste.py          # cria ./Pasta_teste e mostra o resultado esperado
python Organizador_Arquivo_Python/main.py      # informe o caminho de Pasta_teste
```

Rodar o gerador de novo recria o cenário do zero. A pasta `Pasta_teste/` fica fora do Git.

### Testes e checks (os mesmos do CI)

```bash
pip install -r requirements-dev.txt
ruff format --check .   # formatação
ruff check .            # lint
mypy                    # typecheck
python -m pytest        # testes
```

O CI (`.github/workflows/ci.yml`) roda esses checks e o Gitleaks em todo PR e push na `main`.

## 🧠 Conceitos utilizados
- **ETL (Extract, Transform, Load)** com etapas separadas e testáveis
- Manipulação de arquivos com `os`, `shutil` e `csv`
- Estruturas de dados imutáveis com `dataclasses`
- Automação com Python
- Testes automatizados (pytest) e CI com GitHub Actions
