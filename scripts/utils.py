# utils.py
import pandas as pd
import streamlit as st

@st.cache_data
def carregar_dados(path):
    try:
        df = pd.read_csv(path, index_col=0)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame()
