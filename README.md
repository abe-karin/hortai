# 🌱 HortAI — Sua Horta de Varanda

Um aplicativo simples que te ajuda a descobrir **quais ervas e verduras plantar** na sua varanda, janela ou terraço — de acordo com onde você mora e o espaço que você tem.

Sem complicação: você responde a algumas perguntas e o app mostra o que funciona pra você.

---

## De onde vêm os dados?

O HortAI combina uma fonte pública com uma curadoria local:

| Fonte | O que fornece |
|---|---|
| **Wikipedia PT-BR** ([pt.wikipedia.org](https://pt.wikipedia.org)) — fonte pública e gratuita | Descrição botânica de cada planta (nome científico, origem, características) |
| **`data/curadoria.json`** — arquivo local curado manualmente | Dados práticos de cultivo: frequência de rega, nível de dificuldade, regiões do Brasil, temporada ideal e dicas de manejo |

> As descrições botânicas são coletadas automaticamente pelo script `fetch_dados.py` e salvas localmente.
> Para atualizar, basta rodar o script novamente.

---

## O que o app faz

Você escolhe:
- **Onde você mora** (região do Brasil)
- **Quanto tempo quer dedicar** (nível de dificuldade)
- **Quanta luz tem no seu espaço** (sol direto, sol fraco ou meia-sombra)

E o app te mostra:

- 📊 **Resumo rápido** — quantas plantas se encaixam no seu perfil, média de dias entre regas e nível de dificuldade
- 📈 **Gráfico de rega** — visualize de forma simples quais plantas precisam de mais ou menos água
- 📋 **Lista completa** — tabela com todas as plantas recomendadas para o seu caso
- 🔬 **Ficha da planta** — escolha uma planta e veja dicas detalhadas de como cuidar dela

---

## Arquivos do projeto

```
horta/
├── app.py                        # O código principal do aplicativo
├── fetch_dados.py              # Script que coleta os dados e gera os arquivos abaixo
├── data/
│   └── curadoria.json            # Dados agronômicos curados (rega, regiões, manejo etc.)
├── horta_janela_regional.csv     # Gerado pelo fetch_dados.py — lista das plantas
├── manual_tecnico_simples.txt    # Gerado pelo fetch_dados.py — dicas de manejo
├── requirements.txt              # Programas necessários para rodar o app
└── README.md                     # Este arquivo de instruções
```

> 💡 Os arquivos `.csv` e `.txt` são gerados automaticamente pelo `fetch_dados.py`.
> Execute-o antes de rodar o app pela primeira vez.

---

## O que tem na lista de plantas

Cada planta na lista tem as seguintes informações:

| Informação | O que significa |
|---|---|
| `planta` | Nome da planta |
| `luz` | Quanto sol ela precisa (Sol pleno, Sol ameno ou Meia-sombra) |
| `rega_dias` | A cada quantos dias você deve regar |
| `perfil` | Uma característica importante sobre ela |
| `dificuldade_escala_1_5` | Dificuldade de cuidar (1 = muito fácil, 5 = exige atenção) |
| `regioes_aptas` | Em quais regiões do Brasil ela se dá bem |
| `temporada_ideal` | Em qual época do ano é melhor plantá-la |

---

## Como rodar o app

### O que você precisa ter instalado

- [Python 3.9 ou mais recente](https://www.python.org/downloads/)
- pip (geralmente já vem junto com o Python)

### Passo 1 — Instalar as dependências

Abra o terminal na pasta do projeto e rode:

```bash
pip install -r requirements.txt
```

### Passo 2 — Coletar os dados (apenas na primeira vez, ou para atualizar)

```bash
python fetch_dados.py
```

Isso vai buscar as descrições botânicas na Wikipedia e gerar os arquivos `horta_janela_regional.csv` e `manual_tecnico_simples.txt`.

### Passo 3 — Iniciar o aplicativo

```bash
streamlit run app.py
```

O app vai abrir automaticamente no seu navegador. Se não abrir, acesse: `http://localhost:8501`

---

## O que está por baixo do capô

| Ferramenta | Para que serve |
|---|---|
| `streamlit` | Cria a tela do aplicativo no navegador |
| `pandas` | Lê e filtra a lista de plantas |
| `matplotlib` | Desenha os gráficos |
| `seaborn` | Deixa os gráficos com visual mais bonito |
| `requests` + `beautifulsoup4` | Coleta os dados externos no `fetch_dados.py` |

---

## Limitações atuais

- O app vem com **12 plantas** cadastradas. Para adicionar novas, edite `data/curadoria.json` (seguindo o formato das entradas existentes) e rode `python fetch_dados.py` novamente.
- A coleta de dados depende de conexão com a internet. Se a Wikipedia estiver fora do ar, o script avisa e pula a planta sem descrição.
- As descrições botânicas são o primeiro parágrafo da Wikipedia PT-BR. Se uma planta não tiver artigo em português, a descrição ficará em branco.
- As dicas de cuidado ficam no arquivo `manual_tecnico_simples.txt`. Cada linha começa com `[Nome da Planta]` para o app conseguir exibi-la corretamente.
