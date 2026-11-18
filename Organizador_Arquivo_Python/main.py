import os
import shutil

# Mapeamento de extensões para pastas
EXTENSOES = {
    'PDFs': ['.pdf'],
    'Imagens': ['.jpg', '.jpeg', '.png', '.gif'],
    'Planilhas': ['.xlsx', '.xls', '.csv'],
    'Textos': ['.txt', '.docx'],
    'Compactados': ['.zip', '.rar'],
}


def criar_pasta(caminho):
    if not os.path.exists(caminho):
        os.makedirs(caminho)


def caminho_disponivel(pasta_destino, arquivo):
    """Devolve um caminho livre em pasta_destino, sem sobrescrever nada.

    Se 'foto.png' já existe, tenta 'foto (1).png', 'foto (2).png'...
    """
    nome, extensao = os.path.splitext(arquivo)
    candidato = os.path.join(pasta_destino, arquivo)
    contador = 1
    while os.path.exists(candidato):
        candidato = os.path.join(pasta_destino, f'{nome} ({contador}){extensao}')
        contador += 1
    return candidato


def organizar_arquivos(pasta_origem):
    arquivos = os.listdir(pasta_origem)

    for arquivo in arquivos:
        caminho_arquivo = os.path.join(pasta_origem, arquivo)

        if os.path.isfile(caminho_arquivo):
            _, extensao = os.path.splitext(arquivo)

            for pasta, extensoes in EXTENSOES.items():
                if extensao.lower() in extensoes:
                    pasta_destino = os.path.join(pasta_origem, pasta)
                    criar_pasta(pasta_destino)
                    destino = caminho_disponivel(pasta_destino, arquivo)
                    try:
                        shutil.move(caminho_arquivo, destino)
                    except OSError as erro:
                        print(f'Erro ao mover {arquivo}: {erro}')
                        break

                    novo_nome = os.path.basename(destino)
                    if novo_nome == arquivo:
                        print(f'Movido: {arquivo} → {pasta}')
                    else:
                        print(f'Movido: {arquivo} → {pasta} (já existia; salvo como "{novo_nome}")')
                    break


def main():
    pasta = input('Digite o caminho da pasta a ser organizada: ').strip()

    if os.path.exists(pasta):
        organizar_arquivos(pasta)
        print('\nOrganização concluída!')
    else:
        print('Pasta não encontrada.')


if __name__ == '__main__':
    main()
