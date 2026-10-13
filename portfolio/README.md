# Portfólio — Douglas de Oliveira (estilo da capa, 16:9)

Portfólio em 10 páginas, 16:9 (960 × 540 pt), com fundo azul-marinho em degradê, colagem tingida em azul, luz à direita, retrato com brilho e tipografia Montserrat.

## Arquivos

- `Portfolio Douglas de Oliveira - Estilo Capa 16x9.pdf` — PDF final.
- `build_portfolio_cover_style.py` — gera o PDF a partir dos assets (requer `reportlab`, `pillow` e `numpy`).
- `prepare_assets.py` — extrai as imagens do PDF original (`../Portfolio Douglas de Oliveira.pdf`), aplicando as máscaras de transparência (requer `pymupdf`).
- `assets/` — fotos, posts, logos e prints de sites.
- `fonts/` — Montserrat (licença SIL OFL em `fonts/OFL-Montserrat-LICENSE.txt`).

## Como gerar

```bash
pip install reportlab pillow numpy
python3 portfolio/build_portfolio_cover_style.py
```

Para regenerar os assets a partir do PDF original (opcional): `pip install pymupdf && python3 portfolio/prepare_assets.py`.

Para editar textos, altere as chamadas `text(...)` e `paragraph(...)` em `build_portfolio_cover_style.py` e rode o script novamente.
