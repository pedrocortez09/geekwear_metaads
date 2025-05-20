# data_processing.py
import pandas as pd

# ========================================== FUNÇÕES TRATAMENTO DADOS ==========================================

def tratar_datas_crm_ads(df_ads: pd.DataFrame, df_crm: pd.DataFrame):
    # Tratamento de datas para df_ads
    if 'data' in df_ads.columns:
        df_ads['data'] = pd.to_datetime(df_ads['data'], errors='coerce')

    # Tratamento de datas para df_crm
    for col in ['ultima_interacao', 'data_captura', 'data_venda']:
        if col in df_crm.columns:
            df_crm[col] = pd.to_datetime(df_crm[col], errors='coerce')

    return df_ads, df_crm


# ========================================== FUNÇÕES FILTRO DADOS ==========================================

def obter_limites_datas(df_ads, df_crm):
    """Retorna as datas mínima e máxima combinadas de ads e crm"""
    min_data = min(df_ads['data'].min(), df_crm['data_captura'].min())
    max_data = max(df_ads['data'].max(), df_crm['data_captura'].max())
    return min_data, max_data


def filtrar_metaads(df, start_date, end_date, campanhas, generos, idades):
    """Filtra o DataFrame do Meta Ads com base nos filtros selecionados"""
    return df[
        (df['data'].between(start_date, end_date)) &
        (df['campanha'].isin(campanhas)) &
        (df['sexo'].isin(generos)) &
        (df['idade'].isin(idades))
    ]


def filtrar_crm(df, start_date, end_date, canais, campanhas_origem):
    """Filtra o DataFrame do CRM com base nos filtros selecionados"""
    return df[
        (df['data_captura'].between(start_date, end_date)) &
        (df['canal_origem'].isin(canais)) &
        (df['campanha_origem'].isin(campanhas_origem))
    ]

# ========================================== FUNÇÕES CALCULO INDICADORES ==========================================

def calcular_metricas_media(df):
    """Retorna CTR, CPC e CPA médios"""
    ctr_medio = df['ctr (%)'].mean()
    cpc_medio = df['cpc (R$)'].mean()
    cpa_medio = df['cpa (R$)'].mean()
    return ctr_medio, cpc_medio, cpa_medio


def calcular_taxa_conversao_geral(df):
    """Calcula taxa de conversão média por campanha"""
    taxa_campanha = df.groupby('campanha').agg({
        'cliques': 'sum',
        'impressoes': 'sum',
        'conversões': 'sum',
        'gasto_total': 'sum'}).reset_index()

    taxa_campanha['taxa_conversao (%)'] = (taxa_campanha['conversões'] / taxa_campanha['cliques'] * 100).round(2)
    return taxa_campanha['taxa_conversao (%)'].mean()


def agrupar_metaads_por_dia(df):
    """Agrupa os dados do Meta Ads por dia"""
    return df.groupby('data').agg({
        'cliques': 'sum',
        'impressoes': 'sum',
        'conversões': 'sum',
        'gasto_total': 'sum'}).reset_index()


def agrupar_metaads_por_campanha(df):
    """Agrupa os dados do Meta Ads por campanha"""
    return df.groupby('campanha').agg({
        'cliques': 'sum',
        'impressoes': 'sum',
        'conversões': 'sum',
        'gasto_total': 'sum'}).reset_index()



def calcular_metricas_diarias(df_metaads, df_crm, dias):
    """Calcula os KPIs diários"""
    gasto_dia = df_metaads.groupby('campanha')['gasto_total'].sum().mean() / dias
    cliques_dia = df_metaads['cliques'].sum() / dias
    impressoes_dia = df_metaads['impressoes'].sum() / dias
    leads_dia = df_crm['lead_id'].nunique() / dias
    compras_dia = df_crm['sale_id'].nunique() / dias
    return gasto_dia, cliques_dia, impressoes_dia, leads_dia, compras_dia


def calcular_metricas_diarias_metaads(df):
    """Adiciona métricas calculadas por dia ao DataFrame agrupado"""
    df['ctr (%)'] = (df['cliques'] / df['impressoes']) * 100
    df['cpc (R$)'] = df.apply(lambda row: row['gasto_total'] / row['cliques'] if row['cliques'] != 0 else 0, axis=1)
    df['ctr (%)'] = pd.to_numeric(df['ctr (%)'], errors='coerce')
    return df


# ======================= ABA VISÃO GERAL =====================================================
def gerar_ranking_campanhas(df, coluna, maior_valor=True):
    """
    Gera ranking de campanhas baseado em uma métrica específica.

    Parâmetros:
    - df: DataFrame com os dados
    - coluna: coluna para ordenação (ex: 'ctr (%)', 'taxa_conversao (%)')
    - maior_valor: bool, se True ordena do maior para o menor

    Retorna:
    - DataFrame formatado
    """
    if coluna == 'taxa_conversao (%)':
        aux = df.groupby('campanha').agg({
            'cliques': 'sum',
            'conversões': 'sum'
        }).reset_index()
        aux[coluna] = (aux['conversões'] / aux['cliques'] * 100).round(2)
        aux = aux[['campanha', coluna]]
    else:
        aux = df.groupby('campanha')[coluna].mean().round(2).reset_index()

    aux = aux.sort_values(by=coluna, ascending=not maior_valor)
    aux[coluna] = aux[coluna].apply(lambda x: f"{x:.2f}".replace('.', ','))
    return aux
