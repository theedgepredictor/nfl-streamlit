import streamlit as st
import pandas as pd
from consts import GLOSSARY

def display_glossary_tab():
    st.subheader("Glossary", anchor=False)
    st.write("""
    All features are based on data up to but not including the week selected. Week 1 features are built using the previous season average.
    """)
    st.dataframe(pd.DataFrame(GLOSSARY))
