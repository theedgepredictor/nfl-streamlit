import streamlit as st
import pandas as pd

from utils import transform_teams_for_current_week
from sklearn.metrics import accuracy_score, mean_absolute_error


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

def display_evaulation_tab(dataset_df, SEASONS):
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



def display_evaulation_tab(dataset_df, SEASONS):
    st.subheader("Evaluations", anchor=False)
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
