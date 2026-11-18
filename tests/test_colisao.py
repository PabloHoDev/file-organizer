"""Regressão da issue #2: colisão de nome no destino não pode abortar nem perder dados."""

from main import organizar_arquivos


def test_colisao_renomeia_sem_sobrescrever(tmp_path):
    (tmp_path / 'Imagens').mkdir()
    (tmp_path / 'Imagens' / 'perfil.png').write_bytes(b'antiga')
    (tmp_path / 'perfil.png').write_bytes(b'nova')

    organizar_arquivos(str(tmp_path))

    assert (tmp_path / 'Imagens' / 'perfil.png').read_bytes() == b'antiga'
    assert (tmp_path / 'Imagens' / 'perfil (1).png').read_bytes() == b'nova'
    assert not (tmp_path / 'perfil.png').exists()


def test_colisao_repetida_usa_proximo_numero_livre(tmp_path):
    (tmp_path / 'PDFs').mkdir()
    (tmp_path / 'PDFs' / 'contrato.pdf').write_bytes(b'v1')
    (tmp_path / 'PDFs' / 'contrato (1).pdf').write_bytes(b'v2')
    (tmp_path / 'contrato.pdf').write_bytes(b'v3')

    organizar_arquivos(str(tmp_path))

    assert (tmp_path / 'PDFs' / 'contrato (2).pdf').read_bytes() == b'v3'
    assert (tmp_path / 'PDFs' / 'contrato.pdf').read_bytes() == b'v1'
    assert (tmp_path / 'PDFs' / 'contrato (1).pdf').read_bytes() == b'v2'


def test_colisao_nao_interrompe_os_demais_arquivos(tmp_path):
    (tmp_path / 'Imagens').mkdir()
    (tmp_path / 'Imagens' / 'a.png').write_bytes(b'antiga')
    for nome in ['a.png', 'z_relatorio.pdf', 'z_vendas.xlsx']:
        (tmp_path / nome).write_bytes(b'x')

    organizar_arquivos(str(tmp_path))

    assert (tmp_path / 'PDFs' / 'z_relatorio.pdf').exists()
    assert (tmp_path / 'Planilhas' / 'z_vendas.xlsx').exists()
    assert list(tmp_path.glob('*.*')) == []  # nada sobrou na raiz
