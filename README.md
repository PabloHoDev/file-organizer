# 📁 Organizador de Arquivos em Python

📦 organizador-arquivos
 ┣ 📄 main.py
 ┣ 📄 README.md
 ┗ 📂 pasta_teste

Script em Python para organizar automaticamente arquivos de uma pasta com base em suas extensões.

## 🚀 Funcionalidades
- Organização automática por tipo de arquivo
- Criação de pastas se não existirem
- Suporte a PDFs, imagens, planilhas, textos e arquivos compactados
- Nunca sobrescreve: se o destino já tem um arquivo com o mesmo nome, o novo vira `nome (1).ext`

## 🧪 Como testar com um cenário pronto

O script `scripts/gerar_cenario_teste.py` cria uma pasta bagunçada que imita uma pasta de
Downloads real, incluindo casos de borda (extensão em maiúsculas, acentos, arquivos sem
extensão, extensões desconhecidas, subpastas e colisão de nome no destino).

```bash
python scripts/gerar_cenario_teste.py          # cria ./Pasta_teste e mostra o resultado esperado
python Organizador_Arquivo_Python/main.py      # informe o caminho de Pasta_teste
```

Rodar o gerador de novo recria o cenário do zero. A pasta `Pasta_teste/` fica fora do Git.

### Testes automatizados

```bash
pip install pytest
python -m pytest
```

## 🧠 Conceitos utilizados
- Manipulação de arquivos
- Automação com Python
- Bibliotecas os e shutil
- Estruturas de Dados
