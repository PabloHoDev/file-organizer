"""Testes de cada etapa do pipeline ETL (Extract → Transform → Load)."""

import csv
import os

from main import (
    PASTA_RELATORIOS,
    carregar,
    extrair,
    organizar_arquivos,
    salvar_relatorio,
    transformar,
)

# ---------------------------------------------------------------- Extract


def test_extrair_coleta_metadados_e_ignora_subpastas(tmp_path):
    (tmp_path / 'Contrato.PDF').write_bytes(b'12345')
    (tmp_path / 'subpasta').mkdir()
    (tmp_path / 'subpasta' / 'dentro.txt').write_bytes(b'x')

    arquivos = extrair(str(tmp_path))

    assert len(arquivos) == 1
    assert arquivos[0].nome == 'Contrato.PDF'
    assert arquivos[0].extensao == '.pdf'  # normalizada
    assert arquivos[0].tamanho_bytes == 5


# -------------------------------------------------------------- Transform


def test_transformar_nao_toca_no_disco(tmp_path):
    (tmp_path / 'nota.txt').write_bytes(b'x')

    plano = transformar(extrair(str(tmp_path)), str(tmp_path))

    assert [m.categoria for m in plano] == ['Textos']
    assert (tmp_path / 'nota.txt').exists()
    assert not (tmp_path / 'Textos').exists()


def test_transformar_ignora_extensoes_desconhecidas(tmp_path):
    for nome in ['musica.mp3', 'LEIAME', 'backup.tar.gz']:
        (tmp_path / nome).write_bytes(b'x')

    assert transformar(extrair(str(tmp_path)), str(tmp_path)) == []


def test_transformar_nao_repete_destino_dentro_do_plano(tmp_path):
    # 'perfil.png' colide com o que já está em Imagens/ e seria renomeado para
    # 'perfil (1).png' — exatamente o nome de outro arquivo da raiz.
    (tmp_path / 'Imagens').mkdir()
    (tmp_path / 'Imagens' / 'perfil.png').write_bytes(b'antiga')
    (tmp_path / 'perfil.png').write_bytes(b'nova')
    (tmp_path / 'perfil (1).png').write_bytes(b'outra')

    plano = transformar(extrair(str(tmp_path)), str(tmp_path))
    destinos = [os.path.basename(m.destino) for m in plano]

    assert len(destinos) == len(set(destinos)) == 2


# ------------------------------------------------------------------- Load


def test_carregar_preserva_todos_os_conteudos(tmp_path):
    (tmp_path / 'Imagens').mkdir()
    (tmp_path / 'Imagens' / 'perfil.png').write_bytes(b'antiga')
    (tmp_path / 'perfil.png').write_bytes(b'nova')
    (tmp_path / 'perfil (1).png').write_bytes(b'outra')

    resultados = carregar(transformar(extrair(str(tmp_path)), str(tmp_path)))

    assert all(r.status == 'movido' for r in resultados)
    conteudos = sorted(p.read_bytes() for p in (tmp_path / 'Imagens').iterdir())
    assert conteudos == [b'antiga', b'nova', b'outra']


def test_relatorio_csv_registra_a_execucao(tmp_path):
    (tmp_path / 'vendas.xlsx').write_bytes(b'1234')
    resultados = carregar(transformar(extrair(str(tmp_path)), str(tmp_path)))

    caminho = salvar_relatorio(resultados, str(tmp_path))

    with open(caminho, encoding='utf-8-sig', newline='') as f:
        linhas = list(csv.DictReader(f, delimiter=';'))
    assert linhas == [
        {
            'arquivo': 'vendas.xlsx',
            'extensao': '.xlsx',
            'tamanho_bytes': '4',
            'categoria': 'Planilhas',
            'destino': os.path.join('Planilhas', 'vendas.xlsx'),
            'status': 'movido',
            'erro': '',
        }
    ]


# --------------------------------------------------------------- Pipeline


def test_pipeline_salva_relatorio_fora_da_raiz_e_rodar_de_novo_nao_o_move(tmp_path):
    (tmp_path / 'clientes.csv').write_bytes(b'a;b')

    organizar_arquivos(str(tmp_path))
    organizar_arquivos(str(tmp_path))  # segunda execução: nada a fazer

    relatorios = list((tmp_path / PASTA_RELATORIOS).iterdir())
    assert len(relatorios) == 1  # sem movimentos, não gera relatório vazio
    assert [p.name for p in (tmp_path / 'Planilhas').iterdir()] == ['clientes.csv']
