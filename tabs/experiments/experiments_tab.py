import streamlit as st
import os

from sklearn.metrics import accuracy_score, mean_absolute_error
from consts import GLOSSARY
from loaders import load_feature_store
from streamlit_controller import STYLE
import pandas as pd
import nbformat
from nbconvert import HTMLExporter
import datetime

def load_notebook_as_html(notebook_path):
    # Read the notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = nbformat.read(f, as_version=4)

    # Convert the notebook to markdown using nbconvert
    exporter = HTMLExporter()
    html_body, _ = exporter.from_notebook_node(notebook)
    return html_body


def display_experiments_tab(NOTEBOOK_FOLDER):
    st.subheader("Experiments", anchor=False)
    notebook_files = [f for f in os.listdir(NOTEBOOK_FOLDER) if f.endswith('.ipynb')]
    selected_notebook = st.selectbox("Select an experiment:", notebook_files)
    if selected_notebook:
        notebook_path = os.path.join(NOTEBOOK_FOLDER, selected_notebook)
        notebook_html = load_notebook_as_html(notebook_path)
        st.components.v1.html(notebook_html, height=1000, scrolling=True)
