import plotly.express as px
import pandas as pd

# 📊 Gráfico de barras
def grafico_barras(df, eixo_x, eixo_y, hue=None, titulo="", text_auto=False, **kwargs):
    """
    Gera gráfico de barras com ou sem separação por hue (ex: sexo).
    """
    if hue:
        fig = px.bar(df, x=eixo_x, y=eixo_y, color=hue, barmode="group", text_auto=text_auto, title=titulo, **kwargs)
    else:
        fig = px.bar(df, x=eixo_x, y=eixo_y, text_auto=text_auto,  title=titulo)

    fig.update_layout(
        xaxis_title=eixo_x,
        yaxis_title=eixo_y,
        yaxis_tickformat=",",  # vírgula para separador de milhar
    )
    
    fig.update_layout(xaxis_title=eixo_x, yaxis_title=eixo_y)
    return fig


# 📈 Gráfico de linha
def grafico_linha(df, eixo_x, eixo_y, hue=None, titulo="", text_auto=False, **kwargs):
    """
    Gera gráfico de linha para evolução temporal, com ou sem hue.
    """
    if hue:
        fig = px.line(df, x=eixo_x, y=eixo_y, color=hue, markers=True, title=titulo, **kwargs)
    else:
        fig = px.line(df, x=eixo_x, y=eixo_y, markers=True, title=titulo)
    
    fig.update_layout(xaxis_title=eixo_x, yaxis_title=eixo_y)
    return fig


# 🪜 Gráfico de funil (etapas do funil de vendas ou marketing)
def grafico_funil(df, coluna_etapa, titulo="Funil de Leads"):
    """
    Gera gráfico de funil com base nas etapas.
    Espera uma coluna categórica indicando a etapa de cada lead.
    """
    funil = df[coluna_etapa].value_counts().reset_index()
    funil.columns = ['Etapa', 'Quantidade']

    total = funil['Quantidade'].sum()
    funil['Percentual'] = (funil['Quantidade'] / total * 100).round(2)
    
    # Ordena etapas do funil se for possível
    etapas_ordenadas = ["Visita", "Carrinho", "Checkout", "Comprou"]
    funil['Etapa'] = pd.Categorical(funil['Etapa'], categories=etapas_ordenadas, ordered=True)
    funil = funil.sort_values("Etapa")

    fig = px.funnel(funil, x='Quantidade', y='Etapa', title=titulo, hover_data=['Percentual'])
    return fig
