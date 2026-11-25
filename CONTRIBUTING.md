# Como contribuir

Este projeto segue o fluxo de uma equipe de software: todo trabalho nasce numa issue, é feito
numa branch e entra na `main` por Pull Request com CI verde.

## Fluxo

1. **Issue:** abra (ou escolha) uma issue usando os templates de *Bug* ou *Funcionalidade*.
   O roadmap está organizado em [milestones](../../milestones) por versão.
2. **Branch:** a partir da `main` atualizada, no formato `tipo/descricao-curta`:

   ```bash
   git switch main && git pull
   git switch -c feat/dry-run
   ```

   Tipos: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`, `perf`, `hotfix`.
   Uma branch trata de um assunto só.
3. **Commits:** [Conventional Commits](https://www.conventionalcommits.org/pt-br/), em
   português e no imperativo, agrupados por assunto:

   ```
   feat(organizador): adiciona modo --dry-run
   fix(organizador): renomeia arquivo em colisão em vez de abortar
   ```

4. **Pull Request:** preencha o template e referencie a issue (`Closes #N`).
5. **Merge:** com CI verde, via *Squash and merge*. A branch é apagada automaticamente.

## Regras da `main`

A `main` é protegida e está sempre estável:

- não aceita push direto, só Pull Request;
- exige os checks do CI passando e a branch atualizada com a `main`
  (se aparecer *Update branch* no PR, clique e espere o CI);
- exige histórico linear e comentários de revisão resolvidos;
- proíbe force-push e exclusão.

Force-push só na sua própria branch, com `--force-with-lease`. Nunca use `--no-verify`.

## Rodando os checks localmente

São os mesmos do CI:

```bash
pip install -r requirements-dev.txt
ruff format --check .   # formatação (use `ruff format .` para corrigir)
ruff check .            # lint
mypy                    # typecheck
python -m pytest        # testes
```

Para mudanças que afetam a organização, rode também o cenário realista:

```bash
python scripts/gerar_cenario_teste.py
python Organizador_Arquivo_Python/main.py   # informe o caminho de Pasta_teste
```

## Qualidade

- Regra de negócio nova tem teste; bug corrigido ganha um teste que o reproduz.
- Decisões de arquitetura relevantes são registradas em ADR (`docs/adr/NNNN-titulo.md`).
- Nunca coloque segredos, caminhos pessoais ou dados reais em código, testes ou issues.
  O CI roda o Gitleaks em todo PR.

## Versões

Cada milestone concluído vira uma tag [SemVer](https://semver.org/lang/pt-BR/) (`v0.1.0`)
com release notes.
