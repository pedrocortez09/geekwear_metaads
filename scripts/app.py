import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from PIL import Image

from graficos import grafico_barras, grafico_linha, grafico_funil
from utils import carregar_dados
import data_processing as dp

# Configuração inicial
st.set_page_config(
    layout="wide",
    page_title="Dashboard de Campanhas Meta Ads"
)

# Carregamento dos dados
df_ads = carregar_dados("../data/tratados/metaads_data.csv")
df_crm = carregar_dados("../data/tratados/crm_sales_data.csv")

# Tratamento de datas
df_ads, df_crm = dp.tratar_datas_crm_ads(df_ads, df_crm)

# Layout - Logo na sidebar
image = Image.open("../img/logo.png")
st.sidebar.image(image, width=70, use_container_width=True)

# ========================================== FILTROS ============================================================================

# Filtros globais
st.sidebar.header("Filtros")

# Filtro de campanha
campanhas = df_ads['campanha'].dropna().unique()
campanhas1 = df_crm['campanha_origem'].dropna().unique()
campanha_sel = st.sidebar.multiselect("Campanha:", campanhas, default=campanhas)

# Filtro de canal de origem
canais = df_crm['canal_origem'].dropna().unique()
canal_sel = st.sidebar.multiselect("Canal de Origem:", canais, default=canais)

# Filtro por gênero
generos = df_ads['sexo'].dropna().unique()
genero_sel = st.sidebar.multiselect("Gênero:", generos, default=generos)

# Filtro por faixa etária
idades = df_ads['idade'].dropna().unique()
idade_sel = st.sidebar.multiselect("Conjunto de Anúncio:", idades, default=idades)

# Período - usa datas do Meta Ads e do CRM
min_data, max_data = dp.obter_limites_datas(df_ads, df_crm)
data_sel = st.sidebar.date_input("Período", value=(min_data, max_data))
start_date, end_date = pd.to_datetime(data_sel[0]), pd.to_datetime(data_sel[1])

# Métricas e campanhas auxiliares
metricas_disponiveis = ['impressoes', 'cliques', 'conversões', 'gasto_total', 'ctr (%)', 'cpc (R$)', 'cpa (R$)', 'taxa_conversao (%)']
campanha_origem = ['']  # ainda não usado aqui

# Filtragem dos DataFrames
metaads_filtrado = dp.filtrar_metaads(df_ads, start_date, end_date, campanha_sel, genero_sel, idade_sel)
crm_filtrado = dp.filtrar_crm(df_crm, start_date, end_date, canal_sel, campanhas1)


# ========================================== INDICADORES ============================================================================
# Cálculo de dias e indicadores principais
dias = (end_date - start_date).days + 1
ctr_medio, cpc_medio, cpa_medio = dp.calcular_metricas_media(metaads_filtrado)
taxa_conversao = dp.calcular_taxa_conversao_geral(df_ads)

# Agrupamentos
metaads_diario = dp.agrupar_metaads_por_dia(metaads_filtrado)
metaads_campanha = dp.agrupar_metaads_por_campanha(metaads_filtrado)

# Cálculo diário
gasto_dia, cliques_dia, impressoes_dia, leads_dia, compras_dia = dp.calcular_metricas_diarias(metaads_filtrado, crm_filtrado, dias)

# Métricas adicionais por dia
metaads_diario = dp.calcular_metricas_diarias_metaads(metaads_diario)



# ========================================== ABAS DO DASHBOARD ============================================================================
# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(['📊 Visão Geral' , '🏷️ Campanhas', '👥 Públicos', '📝 Funil de Vendas', '📢 Canais de Venda', '📋 Insights'])


# --- ABA 1: VISÃO GERAL ---
with tab1:
    with st.container():
        st.markdown("### 📌 Principais Indicadores")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("CTR médio", f"{ctr_medio:.2f}".replace(".", ",")+"%")
        col2.metric("CPC médio", f"R${cpc_medio:.2f}".replace(".", ","))
        col3.metric("CPA médio", f"R${cpa_medio:.2f}".replace(".", ","))
        col4.metric("Taxa Conversão Média (Conversão/Clique)", f"{taxa_conversao:.2f}".replace(".", ",")+"%")

        col5, col6, col7, col8 = st.columns(4)
        col5.metric("Cliques/dia", f"{int(cliques_dia):,}".replace(",", "."))
        col6.metric("Impressões/dia", f"{int(impressoes_dia):,}".replace(",", "."))
        col7.metric("Leads/dia", f"{int(leads_dia):,}".replace(",",".")) 
        col8.metric("Compras/dia", f"{compras_dia:.0f}")

        st.markdown("""___""")
        

    with st.container():
        st.markdown("### Melhores Campanhas")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("#### CTR")
            st.dataframe(dp.gerar_ranking_campanhas(df_ads, 'ctr (%)', maior_valor=True))

        with col2:
            st.markdown("#### CPC")
            st.dataframe(dp.gerar_ranking_campanhas(df_ads, 'cpc (R$)', maior_valor=False))

        with col3:
            st.markdown("#### CPA")
            st.dataframe(dp.gerar_ranking_campanhas(df_ads, 'cpa (R$)', maior_valor=False))

        with col4:
            st.markdown("#### Taxa Conversão")
            st.dataframe(dp.gerar_ranking_campanhas(df_ads, 'taxa_conversao (%)', maior_valor=True))



# --- ABA 2: VISÃO CAMPANHA ---
with tab2:
    with st.container():
        st.markdown("#### Média Métrica por Campanha")

        metrical_sel = st.selectbox('Selecione a Métrica', metricas_disponiveis, key='metricas_barras')

        # Usa a função refatorada que já trata taxa de conversão e outras métricas
        df_agrupado = dp.gerar_ranking_campanhas(metaads_filtrado, metrical_sel)

        # Corrige a vírgula para ponto (float) para plotagem
        df_agrupado[metrical_sel] = df_agrupado[metrical_sel].apply(lambda x: float(x.replace(',', '.')))

        fig = grafico_barras(df_agrupado, eixo_x='campanha', eixo_y=metrical_sel, text_auto=True)
        st.plotly_chart(fig, use_container_width=True)


        

    with st.container():
        st.markdown("### Campanhas ao longo do tempo")

        metrical_sel = st.selectbox('Selecione a Métrica', metricas_disponiveis, key='metricas_linha')

        if metrical_sel == 'taxa_conversao (%)':
            # Agrupa somando cliques e conversões por dia e campanha, e calcula a taxa
            df_agrupado = metaads_filtrado.groupby(['data', 'campanha']).agg({
                'cliques': 'sum',
                'conversões': 'sum'
            }).reset_index()
            df_agrupado[metrical_sel] = (df_agrupado['conversões'] / df_agrupado['cliques'] * 100).round(2)
        else:
            df_agrupado = metaads_filtrado.groupby(['data', 'campanha'])[[metrical_sel]].mean().reset_index()
            df_agrupado[metrical_sel] = df_agrupado[metrical_sel].round(2)

        fig = grafico_linha(df_agrupado, eixo_x='data', eixo_y=metrical_sel, hue='campanha')
        st.plotly_chart(fig, use_container_width=True)



    with st.container():
        col1, spacer, col2 = st.columns([3, 0.5, 3])
        
        # Agrupamento dos dados de CRM
        df_agrupado = crm_filtrado.groupby(['campanha_origem']).agg({
            'lead_id': 'count',
            'status': lambda x: (x == 'Ganhou').sum(),
            'sale_id': 'count',
            'valor_total': 'sum'
        }).reset_index()

        df_agrupado.columns = ['campanha_origem', 'leads', 'vendas_leads', 'vendas', 'receita_total']
        df_agrupado['taxa_conversao (%)'] = np.round((df_agrupado['vendas'] / df_agrupado['leads']) * 100, 2)

        with col1:
            st.markdown("#### Vendas por Campanha")
            vendas_df = df_agrupado.sort_values('vendas', ascending=False)
            fig = grafico_barras(vendas_df, eixo_x='campanha_origem', eixo_y='vendas', text_auto=True)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### Leads por Campanha")
            leads_df = df_agrupado.sort_values('leads', ascending=False)
            fig = grafico_barras(leads_df, eixo_x='campanha_origem', eixo_y='leads', text_auto=True)
            st.plotly_chart(fig, use_container_width=True)




    with st.container():
        col1, spacer, col2 = st.columns([3, 0.5, 3])

        with col1:
            st.markdown("#### Gasto Total por Campanha")
            gasto_df = metaads_filtrado.groupby('campanha')['gasto_total'].sum().reset_index()
            gasto_df['gasto_total'] = gasto_df['gasto_total'].round(2)
            gasto_df = gasto_df.sort_values('gasto_total', ascending=False)
            fig = grafico_barras(gasto_df, eixo_x='campanha', eixo_y='gasto_total', text_auto=True)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### Total Dias por Campanha")
            # Métricas agrupadas por campanha e publico
            campanha = metaads_filtrado.groupby('campanha').agg({
                'impressoes': 'sum',
                'cliques': 'sum',
                'gasto_total': 'sum',                       
                'conversões': 'sum',                               
                'anuncio': 'count'
            }).reset_index().rename(columns={'anuncio': 'dias_campanha'})
            dias_df = campanha.sort_values('dias_campanha', ascending=False)
            fig = grafico_barras(dias_df, eixo_x='campanha', eixo_y='dias_campanha', text_auto=True)
            st.plotly_chart(fig, use_container_width=True)

# --- ABA 3: VISÃO PÚBLICO ---
with tab3:
    with st.container():
        metrical_sel = st.selectbox('Selecione a Métrica', metricas_disponiveis, key='metricas_publico')

        col1, spacer, col2 = st.columns([3, 0.5, 3])
        
        # Gráfico de barras por sexo e idade
        with col1:
            st.markdown('#### Métrica por público')
            
            color_map = {
                'Mulheres': '#e83e8c',  # rosa
                'Homens': '#007bff'     # azul
            }

            df_agrupado_publico = metaads_filtrado.groupby(['sexo', 'idade'])[metrical_sel].mean().reset_index()
            df_agrupado_publico[metrical_sel] = df_agrupado_publico[metrical_sel].round(2)
            df_agrupado_publico.sort_values(by=metrical_sel, ascending=False, inplace=True)

            fig = grafico_barras(
                df_agrupado_publico,
                eixo_x='idade',
                eixo_y=metrical_sel,
                hue='sexo',
                color_discrete_map=color_map,
                text_auto=True
            )
            st.plotly_chart(fig, use_container_width=True)

        # Heatmap por sexo e idade
        with col2:
            st.markdown("#### Heatmap das métricas")

            df_heat = metaads_filtrado.groupby(['sexo', 'idade'])[metrical_sel].mean().reset_index()

            fig = px.density_heatmap(
                df_heat,
                x='idade',
                y='sexo',
                z=metrical_sel,
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)

    # Linha com média das métricas por dia e sexo
    with st.container():
        st.markdown("#### Média das métricas por dia")
        df_agrupado_dia = metaads_filtrado.groupby(['data', 'sexo'])[[metrical_sel]].mean().reset_index()
        df_agrupado_dia[metrical_sel] = df_agrupado_dia[metrical_sel].round(2)

        fig = grafico_linha(
            df_agrupado_dia,
            eixo_x='data',
            eixo_y=metrical_sel,
            hue='sexo',
            color_discrete_map=color_map
        )
        st.plotly_chart(fig, use_container_width=True)

    # Linha com métrica normalizada por dia e sexo
    with st.container():
        st.markdown("#### Métrica Normalizada por dia")
        df_temp = metaads_filtrado.groupby(['data', 'sexo'])[[metrical_sel]].sum().reset_index()

        df_norm = df_temp.groupby('data').apply(
            lambda x: x.assign(
                **{metrical_sel: x[metrical_sel] / x[metrical_sel].sum() if x[metrical_sel].sum() > 0 else 0}
            )
        ).reset_index(drop=True)

        fig = grafico_linha(
            df_norm,
            eixo_x='data',
            eixo_y=metrical_sel,
            hue='sexo',
            color_discrete_map=color_map
        )
        st.plotly_chart(fig, use_container_width=True)


# --- ABA 4: VISÃO FUNIL VENDAS ---
with tab4:
    with st.container():
        col1, col2 = st.columns(2)

        # Métrica: Tempo médio até a compra
        with col1:
            tempo_medio_compra = np.round(df_crm['dias_para_conversao'].mean(), 0)
            st.metric("Tempo até a compra", f"{tempo_medio_compra:.0f} dias")

        # Métrica: Taxa de conversão
        with col2:
            total_leads = crm_filtrado['lead_id'].nunique()
            leads_compraram = crm_filtrado[crm_filtrado['sale_id'].notnull()]['lead_id'].nunique()

            taxa_conversao = leads_compraram / total_leads if total_leads > 0 else 0
            st.metric("Taxa de Conversão (Compra/Lead)", f"{taxa_conversao:.2%}")

    with st.container():
        st.markdown("### Funil de Vendas")

        # Filtro por campanha
        campanhas_selecionadas = st.multiselect(
            "Campanha:",
            campanhas1,
            default=campanhas1,
            key='funil_vendas'
        )

        crm_filtrado_funil = crm_filtrado[crm_filtrado['campanha_origem'].isin(campanhas_selecionadas)]

        fig = grafico_funil(crm_filtrado_funil, coluna_etapa='etapa_funil', titulo='Funil Leads')
        st.plotly_chart(fig, use_container_width=True)


# --- ABA 5: VISÃO CANAL VENDAS ---
with tab5:
    with st.container():
        # Seleção de métrica
        metrica_selecionada = st.selectbox(
            'Selecione a Métrica',
            metricas_disponiveis,
            key='metricas_canal_origem'
        )

        # Merge de metaads e CRM
        df_merge_canais = pd.merge(
            metaads_filtrado,
            crm_filtrado,
            left_on='campanha',
            right_on='campanha_origem',
            how='inner'
        )

        # Agrupamento por canal e cálculo da métrica média
        df_canais_metricas = (
            df_merge_canais.groupby('canal_origem')[metrica_selecionada]
            .mean()
            .reset_index()
            .sort_values(by=metrica_selecionada, ascending=False)
        )
        df_canais_metricas[metrica_selecionada] = df_canais_metricas[metrica_selecionada].round(2)

        fig = grafico_barras(
            df_canais_metricas,
            eixo_x='canal_origem',
            eixo_y=metrica_selecionada,
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        # Filtro de campanhas
        campanhas_selecionadas = st.multiselect(
            'Filtre a Campanha',
            campanhas1,
            default=campanhas1,
            key='campanhas_canal_origem'
        )

        col1, spacer, col2 = st.columns([3, 0.5, 3])

        # Agrupamento de vendas e leads por canal e campanha
        df_canal_campanha = (
            crm_filtrado.groupby(['canal_origem', 'campanha_origem'])
            .agg(Vendas=('sale_id', 'count'), Leads=('lead_id', 'count'))
            .reset_index()
        )
        df_canal_campanha['Taxa Conversão (%)'] = (
            (df_canal_campanha['Vendas'] / df_canal_campanha['Leads']) * 100
        ).round(2)

        with col1:
            st.markdown("#### Vendas por Canal")
            df_vendas_canal = (
                df_canal_campanha[df_canal_campanha['campanha_origem'].isin(campanhas_selecionadas)]
                .groupby('canal_origem')
                .agg(Vendas=('Vendas', 'sum'), Leads=('Leads', 'sum'))
                .reset_index()
                .sort_values(by='Vendas', ascending=False)
            )
            fig = grafico_barras(
                df_vendas_canal,
                eixo_x='canal_origem',
                eixo_y='Vendas',
                text_auto=True
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### Leads por Canal")
            df_leads_canal = df_vendas_canal.sort_values(by='Leads', ascending=False)
            fig = grafico_barras(
                df_leads_canal,
                eixo_x='canal_origem',
                eixo_y='Leads',
                text_auto=True
            )
            st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown("#### Taxa de Conversão (Vendas/Leads)")
        df_taxa_conversao = (
            df_canal_campanha.groupby('canal_origem')
            .agg({'Taxa Conversão (%)': 'mean'})
            .reset_index()
            .sort_values(by='Taxa Conversão (%)', ascending=False)
        )
        df_taxa_conversao['Taxa Conversão (%)'] = df_taxa_conversao['Taxa Conversão (%)'].round(2)

        fig = grafico_barras(
            df_taxa_conversao,
            eixo_x='canal_origem',
            eixo_y='Taxa Conversão (%)',
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)


# --- ABA 6: RECOMENDAÇÕES E INSIGHTS ---
with tab6:
    st.title("📊 Recomendações e Insights Estratégicos")

    with st.container():
        st.markdown("### 📌 Destaques de Desempenho")
        st.success("Canal **Email** teve a maior taxa de conversão: **32,6%**.")
        st.warning("Campanha **Acessórios** Possui um boa taxa de cliques, porém não gera vendas nem leads.")
        st.info("Tempo médio até a compra: **5 dias**.")

    with st.container():
        st.markdown("### ✅ Recomendações de Ação")
        # Lista de sugestões com markdown
        st.markdown("- Rever campanha Acessórios para gerar leads.")
        st.markdown("- Vamos investir em E-mails. Canal que possui maior taxa de conversão de leads para vendas.")
        st.markdown("- Atrair mulheres tem um custo mais baixo, vamos anunciar segmentado para esse público")

    with st.container():
        st.markdown("### 🚨 Alertas e Oportunidades")
        if taxa_conversao < 0.1:
            st.error("🚨 Taxa de conversão geral está abaixo de 10%. Reveja os filtros de qualificação de leads.")
        else:
            st.info("Taxa de conversão geral está dentro do Padrão.")

        if tempo_medio_compra > 7:
            st.warning(f"⏱ Tempo médio até a compra está elevado ({tempo_medio_compra:.0f} dias). Considere lead perdido.")
        else:
            st.info("Tempo médio até a compra está normal")







