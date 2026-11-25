"""Organizador de arquivos estruturado como um pipeline ETL.

- Extract:   lê a pasta e coleta os metadados de cada arquivo.
- Transform: classifica por categoria e monta o plano de movimentação,
             resolvendo colisões de nome. Não toca no disco.
- Load:      executa o plano e grava um relatório CSV da execução.
"""

import csv
import os
import shutil
from dataclasses import dataclass
from datetime import datetime

# Mapeamento de extensões para pastas
EXTENSOES = {
    'PDFs': ['.pdf'],
    'Imagens': ['.jpg', '.jpeg', '.png', '.gif'],
    'Planilhas': ['.xlsx', '.xls', '.csv'],
    'Textos': ['.txt', '.docx'],
    'Compactados': ['.zip', '.rar'],
}

# Subpasta onde ficam os relatórios. Subpastas não são organizadas, então o
# próprio relatório (.csv) nunca é movido para Planilhas/.
PASTA_RELATORIOS = '_relatorios'


@dataclass(frozen=True)
class ArquivoEncontrado:
    """Registro extraído da pasta (saída do Extract)."""

    nome: str
    caminho: str
    extensao: str
    tamanho_bytes: int


@dataclass(frozen=True)
class Movimento:
    """Um passo do plano de organização (saída do Transform)."""

    arquivo: ArquivoEncontrado
    categoria: str
    destino: str

    @property
    def renomeado(self) -> bool:
        return os.path.basename(self.destino) != self.arquivo.nome


@dataclass(frozen=True)
class Resultado:
    """O que aconteceu com cada movimento (saída do Load)."""

    movimento: Movimento
    status: str  # 'movido' ou 'erro'
    erro: str = ''


# ---------------------------------------------------------------- Extract


def extrair(pasta_origem: str) -> list[ArquivoEncontrado]:
    """Lista os arquivos da raiz da pasta (subpastas são ignoradas)."""
    arquivos = []
    for nome in sorted(os.listdir(pasta_origem)):
        caminho = os.path.join(pasta_origem, nome)
        if os.path.isfile(caminho):
            _, extensao = os.path.splitext(nome)
            arquivos.append(
                ArquivoEncontrado(
                    nome=nome,
                    caminho=caminho,
                    extensao=extensao.lower(),
                    tamanho_bytes=os.path.getsize(caminho),
                )
            )
    return arquivos


# -------------------------------------------------------------- Transform


def categoria_de(extensao: str) -> str | None:
    for categoria, extensoes in EXTENSOES.items():
        if extensao.lower() in extensoes:
            return categoria
    return None


def caminho_disponivel(pasta_destino: str, arquivo: str, reservados: set[str] | None = None) -> str:
    """Devolve um caminho livre em pasta_destino, sem sobrescrever nada.

    Se 'foto.png' já existe (no disco ou reservado no plano), tenta
    'foto (1).png', 'foto (2).png'...
    """
    reservados = reservados if reservados is not None else set()
    nome, extensao = os.path.splitext(arquivo)
    candidato = os.path.join(pasta_destino, arquivo)
    contador = 1
    while os.path.exists(candidato) or os.path.normcase(candidato) in reservados:
        candidato = os.path.join(pasta_destino, f'{nome} ({contador}){extensao}')
        contador += 1
    return candidato


def transformar(arquivos: list[ArquivoEncontrado], pasta_origem: str) -> list[Movimento]:
    """Monta o plano: para onde cada arquivo reconhecido deve ir."""
    plano = []
    reservados: set[str] = set()
    for arquivo in arquivos:
        categoria = categoria_de(arquivo.extensao)
        if categoria is None:
            continue  # extensão desconhecida: fica onde está
        pasta_destino = os.path.join(pasta_origem, categoria)
        destino = caminho_disponivel(pasta_destino, arquivo.nome, reservados)
        reservados.add(os.path.normcase(destino))
        plano.append(Movimento(arquivo=arquivo, categoria=categoria, destino=destino))
    return plano


# ------------------------------------------------------------------- Load


def carregar(plano: list[Movimento]) -> list[Resultado]:
    """Executa o plano. Um erro em um arquivo não interrompe os demais."""
    resultados = []
    for movimento in plano:
        nome = movimento.arquivo.nome
        try:
            os.makedirs(os.path.dirname(movimento.destino), exist_ok=True)
            if os.path.exists(movimento.destino):
                raise FileExistsError(f'destino já existe: {movimento.destino}')
            shutil.move(movimento.arquivo.caminho, movimento.destino)
        except OSError as erro:
            print(f'Erro ao mover {nome}: {erro}')
            resultados.append(Resultado(movimento, 'erro', str(erro)))
            continue

        if movimento.renomeado:
            novo_nome = os.path.basename(movimento.destino)
            print(f'Movido: {nome} → {movimento.categoria} (já existia; salvo como "{novo_nome}")')
        else:
            print(f'Movido: {nome} → {movimento.categoria}')
        resultados.append(Resultado(movimento, 'movido'))
    return resultados


def salvar_relatorio(resultados: list[Resultado], pasta_origem: str) -> str:
    """Grava o relatório CSV da execução e devolve o caminho dele."""
    pasta = os.path.join(pasta_origem, PASTA_RELATORIOS)
    os.makedirs(pasta, exist_ok=True)
    carimbo = datetime.now().strftime('%Y%m%d_%H%M%S')
    caminho = caminho_disponivel(pasta, f'organizacao_{carimbo}.csv')

    # utf-8-sig e ';' para abrir direto no Excel em português
    with open(caminho, 'w', newline='', encoding='utf-8-sig') as arquivo_csv:
        escritor = csv.writer(arquivo_csv, delimiter=';')
        escritor.writerow(
            ['arquivo', 'extensao', 'tamanho_bytes', 'categoria', 'destino', 'status', 'erro']
        )
        for r in resultados:
            m = r.movimento
            escritor.writerow(
                [
                    m.arquivo.nome,
                    m.arquivo.extensao,
                    m.arquivo.tamanho_bytes,
                    m.categoria,
                    os.path.relpath(m.destino, pasta_origem),
                    r.status,
                    r.erro,
                ]
            )
    return caminho


# --------------------------------------------------------------- Pipeline


def organizar_arquivos(pasta_origem: str) -> list[Resultado]:
    """Roda o pipeline completo: Extract → Transform → Load."""
    arquivos = extrair(pasta_origem)
    plano = transformar(arquivos, pasta_origem)
    resultados = carregar(plano)
    if resultados:
        relatorio = salvar_relatorio(resultados, pasta_origem)
        print(f'\nRelatório salvo em: {relatorio}')
    return resultados


def main() -> None:
    pasta = input('Digite o caminho da pasta a ser organizada: ').strip().strip('"')

    # Entrada vazia não pode virar "pasta atual" por engano.
    if pasta and os.path.isdir(pasta):
        organizar_arquivos(os.path.normpath(pasta))
        print('\nOrganização concluída!')
    else:
        print('Pasta não encontrada.')


if __name__ == '__main__':
    main()
