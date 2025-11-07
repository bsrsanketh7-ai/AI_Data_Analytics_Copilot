import pandas as pd
import plotly.express as px
import streamlit as st

def extract_schema(df: pd.DataFrame):
    types = {}
    for c in df.columns:
        types[c] = str(df[c].dtype)
    return types

def render_result(result):
    if isinstance(result, pd.DataFrame):
        st.write(result)
        if not result.empty:
            try:
                # Try a wide table as well
                st.plotly_chart(px.bar(result.reset_index().melt(id_vars=result.index.names if result.index.names else None)), use_container_width=True)
            except Exception:
                pass
    elif isinstance(result, pd.Series):
        st.write(result)
        try:
            st.plotly_chart(px.line(result.reset_index()), use_container_width=True)
        except Exception:
            pass
    else:
        st.write(result)
