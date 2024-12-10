# Gestão de Risco e Derivativos na Indústria Açucareira

## Descrição
Este projeto visa auxiliar na gestão de risco da indústria açucareira, utilizando estratégias de proteção cambial, fixações e operações no mercado de opções. O sistema foi desenvolvido em Python e Streamlit, com o objetivo de fornecer uma ferramenta para a análise e simulação de riscos relacionados à volatilidade dos preços do açúcar e do dólar.

A volatilidade nos mercados financeiros pode afetar diretamente os resultados de uma usina de açúcar, e a implementação de estratégias como contratos futuros, swaps e opções ajuda a mitigar os riscos financeiros.

## Funcionalidades
- Proteção Cambial: Simulação de contratos futuros de câmbio para garantir uma taxa de câmbio previsível para exportações.
Fixações: Uso de contratos a termo e swaps para garantir um preço mínimo para a produção de açúcar.
- Mercado de Opções: Simulação de opções de venda e compra de açúcar, permitindo flexibilidade para proteger-se contra movimentos desfavoráveis nos preços.
Análises Estatísticas: Cálculo de médias, volatilidade e projeções para os preços do açúcar.
- Simulação de Monte Carlo: Geração de cenários futuros com base na distribuição dos retornos - 
- históricos dos preços do açúcar.
## Tecnologias Utilizadas
- Python: Linguagem de programação utilizada para o desenvolvimento do algoritmo.
- Streamlit: Framework para criação da interface interativa.
- Pandas: Manipulação e análise de dados financeiros.
- yFinance: Obtenção de dados históricos de preços do açúcar e do dólar.
- NumPy: Cálculos matemáticos e estatísticos.
- Matplotlib/Plotly: Visualização dos dados e gráficos interativos.
## Requisitos
Python 3.12 ou superior
Bibliotecas:
streamlit
yfinance
pandas
numpy
matplotlib
plotly

## Instalação
Clone este repositório para o seu ambiente local
Link com o site da Streamlit

## Instale as dependências:
pip install -r requirements.txt

## Executando o Projeto
Execute o site Streamlit e link o rebositorio do github

## Como Utilizar
Selecione o ativo: Escolha o ativo desejado, como "SBV24.NYB", "USDBRL=X", etc.
Defina o intervalo de datas: Selecione um período para análise.
Escolha o indicador: Selecione o indicador que deseja analisar, como EWMA, CCI, MACD, etc.
Calcule e visualize os resultados: Após definir as opções, clique no botão "Calcular" para gerar as análises e gráficos interativos.

## Colaboradores
Gabriel Canuto de Alencar

## Licença
Este projeto está licenciado sob a MIT License.
https://share.streamlit.io/user/coluno
