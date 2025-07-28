
import os
import streamlit as st
from sklearn.metrics import accuracy_score, mean_absolute_error
from consts import GLOSSARY
from loaders import load_feature_store
from streamlit_controller import STYLE
import pandas as pd
import nbformat
from nbconvert import HTMLExporter
import datetime

# Import tab modules
from tabs.venues.venues_tab import display_venues_tab
from tabs.teams.teams_tab import display_team_tab
from tabs.events.events_tab import display_event_tab
from tabs.evaluation.evaluation_tab import display_evaulation_tab
from tabs.experiments.experiments_tab import display_experiments_tab
from tabs.glossary.glossary_tab import display_glossary_tab

def find_year_for_season( date: datetime.datetime = None):
    """
    Find the year for a specific season based on the league and date.

    Args:
        league (ESPNSportTypes): Type of sport.
        date (datetime.datetime): Date for the sport (default is None).

    Returns:
        int: Year for the season.
    """
    SEASON_START_MONTH = {

        "NFL": {'start': 6, 'wrap': False},
    }
    if date is None:
        today = datetime.datetime.utcnow()
    else:
        today = date
    start = SEASON_START_MONTH["NFL"]['start']
    wrap = SEASON_START_MONTH["NFL"]['wrap']
    if wrap and start - 1 <= today.month <= 12:
        return today.year + 1
    elif not wrap and start == 1 and today.month == 12:
        return today.year + 1
    elif not wrap and not start - 1 <= today.month <= 12:
        return today.year - 1
    else:
        return today.year

# Path to the folder containing your Jupyter Notebooks
SEASONS = list(range(2019, find_year_for_season() + 1))
NOTEBOOK_FOLDER = './experiments/'  # Change this to the correct path
st.set_page_config(layout='wide')

# Function to read and convert Jupyter Notebook to markdown


def main():
    st.title('The Edge Predictor NFL Statistics', anchor=False)
    # Load data
    dataset_df, folded_df = load_feature_store(SEASONS)

    ### Define tabs for Team, Event
    event_tab, team_tab, evaluations_tab, experiments_tab, glossary_tab, venues_tab = st.tabs([
        "Events",
        "Teams",
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