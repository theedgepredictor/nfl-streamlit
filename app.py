import os

import streamlit as st
# Streamlit App
from sklearn.metrics import accuracy_score, mean_absolute_error

from consts import GLOSSARY
from loaders import load_feature_store
from streamlit_controller import STYLE
import pandas as pd
import nbformat
from nbconvert import HTMLExporter
from utils import find_year_for_season

# Path to the folder containing your Jupyter Notebooks
SEASONS = list(range(2019, find_year_for_season() + 1))
NOTEBOOK_FOLDER = './experiments/'  # Change this to the correct path
st.set_page_config(layout='wide')

# Function to read and convert Jupyter Notebook to markdown
def load_notebook_as_html(notebook_path):
    # Read the notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = nbformat.read(f, as_version=4)

    # Convert the notebook to markdown using nbconvert
    exporter = HTMLExporter()
    html_body, _ = exporter.from_notebook_node(notebook)
    return html_body

def transform_teams_for_current_week(folded_df, season, week):
    filtered_df = folded_df[((folded_df['season'] == season) & (folded_df['week'] == week))].copy()
    if week == 1:
        s = folded_df[((folded_df['season'] == season-1) & (folded_df['week'] < 18 if season > 2021 else 17))].copy()
    else:
        s = folded_df[((folded_df['season'] == season) & (folded_df['week'] < week))].copy()
    s['avg_points_over_expected'] = s['actual_points'] - s['expected_points']
    s['actual_over_covered'] = s['actual_under_covered'] == 0
    points_over_expected = s.groupby(['team'])['avg_points_over_expected'].mean().sort_values(ascending=False).reset_index()
    covered_spread = s.groupby(['team'])['actual_team_covered_spread'].sum().sort_values(ascending=False).reset_index()
    went_under = s.groupby(['team'])['actual_over_covered'].sum().sort_values(ascending=False).reset_index()

    joiners = [
        points_over_expected,
        covered_spread,
        went_under
    ]
    filtered_df = filtered_df.drop(columns=['actual_under_covered', 'actual_team_covered_spread'])
    for j in joiners:
        filtered_df = pd.merge(filtered_df, j, on=['team'], how='left')
    return filtered_df

def display_team_tab(folded_df):
    st.subheader("Teams", anchor=False)
    season_options = sorted(folded_df['season'].unique())
    default_season_idx = season_options.index(max(season_options))
    season = st.selectbox('Select Season:', season_options, index=default_season_idx, key='team_season')
    # Select week to display
    week_options = sorted(folded_df[folded_df['season'] == season]['week'].unique())
    if season == max(season_options):
        s_df = folded_df[((folded_df['season'] == season)&(folded_df['actual_points'].isnull()))].copy()
        if s_df.shape[0] == 0:
            default_week_idx = week_options.index(max(week_options))
        else:
            default_week_idx = week_options.index(s_df.week.values[0])
    else:
        default_week_idx = week_options.index(max(week_options))

    week = st.selectbox('Select Week:', week_options, index=default_week_idx, key='team_week')


    top_table_cols = [
        'team',
        'expected_points',
        'rating',
        'offensive_rank',
        'defensive_rank',
        'avg_points_over_expected',
        'actual_team_covered_spread',
        'actual_over_covered',
    ]


    st.write(f"Team Ratings Week {week} in the {season} Season")
    filtered_folded_df = transform_teams_for_current_week(folded_df, season, week)
    selected_team = st.dataframe(filtered_folded_df[top_table_cols])

def display_event_tab(dataset_df, folded_df):
    st.subheader("Events", anchor=False)
    # Load data for the 2024 season
    season_options = sorted(dataset_df['season'].unique())
    default_season_idx = season_options.index(max(season_options))
    season = st.selectbox('Select Season:', season_options, index=default_season_idx, key='event_season')
    # Select week to display
    week_options = sorted(dataset_df[dataset_df['season'] == season]['week'].unique())
    if season == max(season_options):
        s_df = dataset_df[((dataset_df['season'] == season)&(dataset_df['actual_away_points'].isnull()))].copy()
        if s_df.shape[0] == 0:
            default_week_idx = week_options.index(max(week_options))
        else:
            default_week_idx = week_options.index(s_df.week.values[0])
    else:
        default_week_idx = week_options.index(max(week_options))

    week = st.selectbox('Select Week:', week_options, index=default_week_idx, key='event_week')

    top_table_cols = [
        'away_rating',
        'away_team',
        'home_rating',
        'home_team',
        'spread_line',
        'expected_spread',
        'actual_away_spread',
        'total_line',
        'expected_total',
        'actual_point_total',
        'away_expected_points',
        'actual_away_points',
        'home_expected_points',
        'actual_home_points',
    ]

    folded_table_cols = [
        'rating',
        'offensive_rank',
        'defensive_rank',
        'actual_team_covered_spread',
        'actual_over_covered',
        'avg_points_over_expected',
        'expected_points',
        'expected_q1_points',
        'expected_q2_points',
        'expected_q3_points',
        'expected_q4_points',
        'expected_q5_points',
        'expected_carries',
        'expected_rushing_yards',
        'expected_rushing_tds',
        'expected_completions',
        'expected_attempts',
        'expected_passing_yards',
        'expected_passing_tds',
        'expected_time_of_possession',
        'expected_turnover',
        'expected_field_goal_made'
    ]

    # Filter games for the selected week
    filtered_df = dataset_df[((dataset_df['season'] == season)&(dataset_df['week'] == week))].copy()
    if season < dataset_df.season.max() or (season == dataset_df.season.max() and week < dataset_df[((dataset_df['season'] == season)&(dataset_df['actual_away_points'].isnull()))].week.max() - 1):
        eval = make_evaluation_report(filtered_df)
        st.dataframe(pd.DataFrame([eval]))

    # Show the games for the selected week
    st.write(f"Games for Week {week} in the {season} Season")
    selected_game = st.dataframe(filtered_df[top_table_cols], selection_mode="single-row")
    if selected_game:
        print(selected_game)

    # Add a select box to choose a game row (based on team names)
    selected_row = st.selectbox('Select a Game:', filtered_df.index)

    # Display selected game row in a context window
    if selected_row is not None:
        st.write(f"Selected Game: {filtered_df.loc[selected_row, 'home_team']} vs {filtered_df.loc[selected_row, 'away_team']}")

        # Display all relevant columns for the selected row
        filtered_folded_df = transform_teams_for_current_week(folded_df, season, week)
        game = filtered_folded_df[filtered_folded_df.game_id == selected_row].copy()
        game.index = game.team
        st.table(game[folded_table_cols].T)  # Transpose to display row as table

def display_experiments_tab():
    st.subheader("Experiments", anchor=False)
    # List available notebooks in the directory
    notebook_files = [f for f in os.listdir(NOTEBOOK_FOLDER) if f.endswith('.ipynb')]

    # Dropdown to select a notebook
    selected_notebook = st.selectbox("Select an experiment:", notebook_files)

    # Load and display the selected notebook
    if selected_notebook:
        notebook_path = os.path.join(NOTEBOOK_FOLDER, selected_notebook)
        notebook_html = load_notebook_as_html(notebook_path)

        # Display the notebook as HTML in Streamlit
        st.components.v1.html(notebook_html, height=1000, scrolling=True)

def display_glossary_tab():
    st.subheader("Glossary", anchor=False)
    st.write(f"""
    All features are based on data up to but not including the week selected. Week 1 features are built using the previous season average.
    """)
    st.dataframe(pd.DataFrame(GLOSSARY))

def did_away_team_cover(spread_line, away_team_spread):
    """Returns True if away team covered the spread"""
    if spread_line < 0:  # Away team is favored
        return away_team_spread > abs(spread_line)
    else:  # Home team is favored
        return away_team_spread < spread_line

def make_evaluation_report(eval_df):
    try:
        # Actual values
        actual_wp = eval_df['actual_away_team_win'].values
        actual_spread = eval_df['actual_away_spread'].values
        actual_total = eval_df['actual_point_total'].values

        # --- Vegas Baseline ---
        vegas_wp = eval_df['spread_line'].apply(lambda x: 1 if x < 0 else 0).values
        vegas_spread = eval_df['spread_line'].values
        vegas_total = eval_df['total_line'].values

        # --- Expected Points Averages ---
        exp_avg_wp = eval_df['expected_spread'].apply(lambda x: 1 if x < 0 else 0).values
        exp_avg_spread = eval_df['expected_spread'].values
        exp_avg_total = eval_df['away_expected_points'].values + eval_df['home_expected_points'].values

        # --- Spread and Total Coverage ---
        eval_df['expected_system_covered_spread'] = (eval_df['away_expected_points'] + eval_df['spread_line'] >= eval_df['home_expected_points'])
        eval_df['expected_system_covered_spread'] = eval_df['expected_system_covered_spread'] == eval_df['actual_away_team_covered_spread']

        eval_df['expected_system_under_covered_total'] = (eval_df['home_expected_points'] + eval_df['away_expected_points'] <= eval_df['total_line'])
        eval_df['expected_system_under_covered_total'] = eval_df['expected_system_under_covered_total'] == eval_df['actual_under_covered']

        return {
            'games': eval_df.shape[0],
            'vegas_wp_accuracy': round(accuracy_score(actual_wp, vegas_wp),4),
            'vegas_spread_mae': round(mean_absolute_error(actual_spread, vegas_spread),4),
            'vegas_total_mae': round(mean_absolute_error(actual_total, vegas_total),4),
            'expected_wp_accuracy': round(accuracy_score(actual_wp, exp_avg_wp),4),
            'expected_spread_mae': round(mean_absolute_error(actual_spread, exp_avg_spread),4),
            'expected_total_mae': round(mean_absolute_error(actual_total, exp_avg_total),4),
            'expected_away_points_mae': round(mean_absolute_error(eval_df['actual_away_points'], eval_df['away_expected_points']),4),
            'expected_home_points_mae': round(mean_absolute_error(eval_df['actual_home_points'], eval_df['home_expected_points']),4),
            'expected_system_correct_spread_percent': round(eval_df['expected_system_covered_spread'].sum() / len(eval_df),4),
            'expected_system_correct_total_percent': round(eval_df['expected_system_under_covered_total'].sum() / len(eval_df), 4)
        }
    except Exception as e:
        return {
            'games': eval_df.shape[0],
            'vegas_wp_accuracy': 0,
            'vegas_spread_mae': 0,
            'vegas_total_mae': 0,
            'expected_wp_accuracy': 0,
            'expected_spread_mae': 0,
            'expected_total_mae': 0,
            'expected_away_points_mae': 0,
            'expected_home_points_mae':0,
            'expected_system_correct_spread_percent':0,
            'expected_system_correct_total_percent': 0,
        }

def display_evaulation_tab(dataset_df):
    st.subheader("Evaluations", anchor=False)
    # Load data for the 2024 season
    # Select season to evaluate

    evals = []

    for season in SEASONS:
        eval_df = dataset_df[(dataset_df['season'] == season) & (dataset_df['actual_away_points'].notnull())].copy()
        if eval_df.shape[0] == 0:
            continue
        eval_report = make_evaluation_report(eval_df)
        eval_report['season'] = str(season)
        evals.append(eval_report)
    full = make_evaluation_report(dataset_df[(dataset_df['actual_away_points'].notnull())].copy())
    full['season'] = 'Full'
    evals.append(full)

    evals = pd.DataFrame(evals)
    evals.index = evals.season
    evals = evals.drop(columns='season')
    st.dataframe(evals)


def main():
    st.title('The Edge Predictor NFL Statistics', anchor=False)
    # Load data
    dataset_df, folded_df = load_feature_store(SEASONS)

    ### Define tabs for Team, Event
    event_tab, team_tab,evaluations_tab, experiments_tab, glossary_tab = st.tabs([
        "Events",
        "Teams",
        "Evaluation",
        "Experiments",
        "Glossary"
    ])
    with event_tab:
        st.markdown(STYLE, unsafe_allow_html=True)
        display_event_tab(dataset_df, folded_df)

    with team_tab:
        st.markdown(STYLE, unsafe_allow_html=True)
        display_team_tab(folded_df)

    with evaluations_tab:
        display_evaulation_tab(dataset_df)

    with experiments_tab:
        display_experiments_tab()



    with glossary_tab:
        st.markdown(STYLE, unsafe_allow_html=True)
        display_glossary_tab()

if __name__ == "__main__":
    main()