# Portfólio — Douglas de Oliveira (estilo Suíço, 16:9)

Versão refeita do portfólio em estilo tipográfico suíço (grid de 12 colunas, Helvetica, preto + azul de destaque), formato 16:9 (960 × 540 pt), 10 páginas.

## Arquivos

- `Portfolio Douglas de Oliveira - Swiss 16x9.pdf` — PDF final.
- `build_portfolio.py` — gera o PDF a partir dos assets (requer `reportlab` e `pillow`).
- `prepare_assets.py` — extrai imagens do PDF original (`../Portfolio Douglas de Oliveira.pdf`), aplicando as máscaras de transparência (requer `pymupdf`).
- `assets/` — imagens extraídas (fotos, posts, logos, prints de sites).

## Como gerar

```bash
pip install reportlab pillow pymupdf   # apenas se for regenerar os assets
python3 portfolio/prepare_assets.py     # opcional
python3 portfolio/build_portfolio.py
```

Para editar textos, altere as chamadas `text(...)` em `build_portfolio.py` e rode o script novamente.

## Versões

- **Estilo Suíço (16:9):** `Portfolio Douglas de Oliveira - Swiss 16x9.pdf`, gerado por `build_portfolio.py`.
- **Estilo da capa (16:9):** `Portfolio Douglas de Oliveira - Estilo Capa 16x9.pdf`, gerado por `build_portfolio_cover_style.py`. Usa fundo azul com degradê, colagem tingida, luz à direita, retrato com brilho e tipografia Montserrat (`fonts/`, licença SIL OFL em `fonts/OFL-Montserrat-LICENSE.txt`).

Para gerar a versão da capa:

```bash
pip install reportlab pillow numpy
python3 portfolio/build_portfolio_cover_style.py
```
