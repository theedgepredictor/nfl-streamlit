
import os
import streamlit as st
from sklearn.metrics import accuracy_score, mean_absolute_error
from consts import GLOSSARY
from loaders import load_feature_store
from streamlit_controller import STYLE
import pandas as pd
import nbformat
from nbconvert import HTMLExporter
from nfl_data_loader.utils.utils import find_year_for_season
# Import tab modules
from tabs.players.players_tab import display_event_player_tab, display_player_tab
from tabs.venues.venues_tab import display_venues_tab
from tabs.teams.teams_tab import display_team_tab
from tabs.events.events_tab import display_event_tab
from tabs.evaluation.evaluation_tab import display_evaulation_tab
from tabs.experiments.experiments_tab import display_experiments_tab
from tabs.glossary.glossary_tab import display_glossary_tab

# Path to the folder containing your Jupyter Notebooks
SEASONS = list(range(2019, find_year_for_season() + 1))
NOTEBOOK_FOLDER = './experiments/'  # Change this to the correct path
st.set_page_config(layout='wide')

# Function to read and convert Jupyter Notebook to markdown


def main():
    st.title('The Edge Predictor NFL Statistics', anchor=False)
    # Load data
    dataset_df, folded_df, player_df = load_feature_store(SEASONS)

    ### Define tabs for Team, Event
    event_tab, team_tab,player_tab,event_player_tab, evaluations_tab, experiments_tab, glossary_tab, venues_tab = st.tabs([
        "Events",
        "Teams",
        "Players",
        "Event Players",
        "Evaluation",
        "Experiments",
        "Glossary",
        "Venues"
    ])

    with event_tab:
        st.markdown(STYLE, unsafe_allow_html=True)
        display_event_tab(dataset_df, folded_df)

    with team_tab:
        st.markdown(STYLE, unsafe_allow_html=True)
        display_team_tab(folded_df)

    with event_player_tab:
        st.markdown(STYLE, unsafe_allow_html=True)
        display_event_player_tab(dataset_df, player_df)

    with player_tab:
        st.markdown(STYLE, unsafe_allow_html=True)
        display_player_tab(player_df)
    with evaluations_tab:
        display_evaulation_tab(dataset_df, SEASONS)

    with experiments_tab:
        display_experiments_tab(NOTEBOOK_FOLDER)

    with glossary_tab:
        st.markdown(STYLE, unsafe_allow_html=True)
        display_glossary_tab()

    with venues_tab:
        display_venues_tab()

if __name__ == "__main__":
    main()