"""Gera uma pasta bagunçada para testar o organizador manualmente.

Simula uma pasta de Downloads real, com casos comuns e casos de borda:
extensões em maiúsculas, nomes com acento e espaço, arquivos sem extensão,
extensões desconhecidas, subpastas e colisão de nome no destino.

Uso:
    python scripts/gerar_cenario_teste.py            # cria em ./Pasta_teste
    python scripts/gerar_cenario_teste.py outra/pasta

Rodar de novo recria o cenário do zero. Por segurança, o script só apaga
uma pasta que ele mesmo criou (identificada pelo arquivo marcador).
"""

import shutil
import sys
from pathlib import Path

MARCADOR = '.cenario_teste'
PASTA_PADRAO = Path(__file__).resolve().parent.parent / 'Pasta_teste'

# (caminho relativo, conteúdo, o que se espera que o organizador faça)
ARQUIVOS = [
    # Casos comuns: um de cada categoria
    ('contrato.pdf', b'%PDF-1.4 fake', 'vai para PDFs/'),
    ('foto_praia.jpg', b'\xff\xd8\xff fake', 'vai para Imagens/'),
    ('logo.png', b'\x89PNG fake', 'vai para Imagens/'),
    ('vendas_2025.xlsx', b'PK fake xlsx', 'vai para Planilhas/'),
    ('clientes.csv', b'nome,email\nAna,ana@exemplo.com\n', 'vai para Planilhas/'),
    ('anotacoes.txt', b'lembrar de pagar o boleto', 'vai para Textos/'),
    ('curriculo.docx', b'PK fake docx', 'vai para Textos/'),
    ('backup_fotos.zip', b'PK fake zip', 'vai para Compactados/'),

    # Casos de borda
    ('FOTO_CELULAR.JPG', b'\xff\xd8\xff fake', 'extensão maiúscula: deve ir para Imagens/'),
    ('Relatório Anual 2025.pdf', b'%PDF-1.4 fake', 'acento e espaço: deve ir para PDFs/'),
    ('backup.tar.gz', b'fake gz', 'extensão desconhecida (.gz): deve ficar na raiz'),
    ('musica.mp3', b'ID3 fake', 'extensão desconhecida: deve ficar na raiz'),
    ('script.py', b'print("oi")\n', 'extensão desconhecida: deve ficar na raiz'),
    ('LEIAME', b'arquivo sem extensao', 'sem extensão: deve ficar na raiz'),
    ('.config_oculta', b'oculto', 'arquivo oculto: deve ficar na raiz'),
    ('projeto/rascunho.txt', b'dentro de subpasta', 'subpasta: não deve ser tocada'),

    # Colisão: já existe um arquivo com o mesmo nome no destino
    ('Imagens/logo_antigo.png', b'\x89PNG versao antiga', 'já estava organizado'),
    ('Imagens/perfil.png', b'\x89PNG versao antiga', 'já estava organizado'),
    ('perfil.png', b'\x89PNG versao NOVA', 'colisão com Imagens/perfil.png: não pode perder dados'),
]


def gerar(destino: Path) -> None:
    if destino.exists():
        if not (destino / MARCADOR).exists() and any(destino.iterdir()):
            sys.exit(
                f'Recusado: {destino} já existe, não está vazia e não foi criada por este '
                'script. Escolha outra pasta.'
            )
        # Limpa só o conteúdo: no Windows a própria pasta pode estar travada
        # (Explorer ou editor aberto nela).
        for item in destino.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

    destino.mkdir(parents=True, exist_ok=True)
    (destino / MARCADOR).write_text('pasta gerada por scripts/gerar_cenario_teste.py\n')

    for relativo, conteudo, _ in ARQUIVOS:
        caminho = destino / relativo
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_bytes(conteudo)

    print(f'Cenário criado em: {destino}\n')
    print('Resultado esperado após rodar o organizador:')
    for relativo, _, esperado in ARQUIVOS:
        print(f'  {relativo:<28} {esperado}')
    print('\nAgora rode: python Organizador_Arquivo_Python/main.py e informe a pasta acima.')


if __name__ == '__main__':
    gerar(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else PASTA_PADRAO)
