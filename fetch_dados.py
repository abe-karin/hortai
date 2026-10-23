"""
fetch_dados.py
--------------
Script de coleta de dados para o Brota.

Estratégia de fontes:
  1. Wikipedia PT-BR REST API  — descrição botânica gratuita, sem autenticação,
     documentada em https://pt.wikipedia.org/api/rest_v1/
  2. data/curadoria.json        — dados agronômicos práticos (rega, dificuldade,
     regiões, temporada, manejo) curados manualmente com base em literatura
     agronômica brasileira.

Uso:
  python fetch_dados.py

Saída:
  horta_janela_regional.csv    — dataset principal do app
  manual_tecnico_simples.txt   — dicas de manejo por planta
"""

import json
import os
import time
import urllib.request
import urllib.parse
import ssl

# ------------------------------------------------------------------
# Configurações
# ------------------------------------------------------------------
CURADORIA_PATH = os.path.join(os.path.dirname(__file__), "data", "curadoria.json")
CSV_OUT = "horta_janela_regional.csv"
TXT_OUT = "manual_tecnico_simples.txt"
WIKI_API = "https://pt.wikipedia.org/api/rest_v1/page/summary/{title}"
DELAY_SEGUNDOS = 0.5  # cortesia para não sobrecarregar a API

# Desabilitar verificação SSL apenas para compatibilidade local
# (Wikipedia usa certificado válido; este contexto é fallback)
_ssl_ctx = ssl.create_default_context()


def buscar_descricao_wikipedia(titulo_wiki: str) -> str:
    """
    Consulta a Wikipedia PT-BR REST API e retorna o extrato resumido da planta.
    Retorna string vazia em caso de falha (rede, 404, etc.).

    Documentação da API: https://pt.wikipedia.org/api/rest_v1/
    Política de uso: https://www.mediawiki.org/wiki/REST_API
    """
    url = WIKI_API.format(title=urllib.parse.quote(titulo_wiki))
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "HortAI/1.0 (horta-varanda; contato: HortAI@exemplo.br)"
        },
    )
    try:
        resp = urllib.request.urlopen(req, timeout=10, context=_ssl_ctx)
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("extract", "").split("\n")[0]  # apenas o 1º parágrafo
    except Exception as exc:
        print(f"  [WARN] Wikipedia falhou para '{titulo_wiki}': {exc}")
        return ""


def gerar_dataset():
    """
    Lê data/curadoria.json, enriquece cada planta com a descrição da Wikipedia
    e grava os arquivos CSV e TXT usados pelo app.
    """
    if not os.path.exists(CURADORIA_PATH):
        print(f"[ERRO] Arquivo de curadoria não encontrado: {CURADORIA_PATH}")
        return

    with open(CURADORIA_PATH, "r", encoding="utf-8") as f:
        curadoria = json.load(f)

    plantas = curadoria["plantas"]
    print(f"Coletando dados para {len(plantas)} plantas...\n")

    linhas_csv = [
        "planta,luz,rega_dias,perfil,dificuldade_escala_1_5,"
        "regioes_aptas,temporada_ideal,descricao_botanica,fonte_botanica"
    ]
    linhas_txt = []

    for planta in plantas:
        nome = planta["planta"]
        wiki_titulo = planta.get("wikipedia", "")

        print(f"  [{nome}] buscando Wikipedia ({wiki_titulo})...")
        descricao = buscar_descricao_wikipedia(wiki_titulo) if wiki_titulo else ""
        fonte = (
            f"https://pt.wikipedia.org/wiki/{urllib.parse.quote(wiki_titulo)}"
            if wiki_titulo and descricao
            else ""
        )

        regioes = planta["regioes_aptas"]
        # Campos que podem conter vírgulas ou aspas são sempre envolvidos em
        # aspas duplas; aspas internas são escapadas duplicando-as ("" = ").
        def csv_field(value: str) -> str:
            escaped = value.replace('"', '""')
            return f'"{escaped}"'

        linhas_csv.append(
            f'{nome},{planta["luz"]},{planta["rega_dias"]},'
            f'{planta["perfil"]},{planta["dificuldade_escala_1_5"]},'
            f'{csv_field(regioes)},{planta["temporada_ideal"]},'
            f'{csv_field(descricao) if descricao else ""},{fonte}'
        )

        linhas_txt.append(f'[{nome}] Manejo: {planta["manejo"]}')

        time.sleep(DELAY_SEGUNDOS)

    # Gravar CSV
    with open(CSV_OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas_csv))
    print(f"\nCSV salvo em: {CSV_OUT}")

    # Gravar TXT
    with open(TXT_OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas_txt))
    print(f"Manual salvo em: {TXT_OUT}")


if __name__ == "__main__":
    gerar_dataset()
