import pandas as pd

from consts import META, VEGAS, TARGETS, POINT_FEATURES, RANKING_FEATURES, JUST_SIMPLE_FEATURES
from utils import df_rename_shift, df_rename_exavg, df_rename_fold

import streamlit as st

def get_event_feature_store(season):
    return pd.read_parquet(f'https://github.com/theedgepredictor/nfl-feature-store/raw/main/data/feature_store/event/regular_season_game/{season}.parquet')

@st.cache_data
def load_feature_store(seasons):
    event_fs = pd.concat([get_event_feature_store(season) for season in seasons], ignore_index=True)
    columns_for_base = META + ['home_elo_pre', 'away_elo_pre'] + VEGAS + TARGETS + ['away_offensive_rank','away_defensive_rank','home_offensive_rank','home_defensive_rank',]
    columns_for_shift = ['team', 'season', 'week', 'is_home'] + POINT_FEATURES + JUST_SIMPLE_FEATURES
    shifted_df = event_fs.copy()
    base_dataset_df = event_fs[columns_for_base].copy()
    del event_fs

    #### Shift Features
    shifted_df = df_rename_shift(shifted_df)[columns_for_shift]

    #### Rename for Expected Average
    t1_cols = [i for i in shifted_df.columns if '_offense' in i and (i not in TARGETS + META) and i.replace('home_', '') in columns_for_shift]
    t2_cols = [i for i in shifted_df.columns if '_defense' in i and (i not in TARGETS + META) and i.replace('away_', '') in columns_for_shift]

    #### Apply Expected Average
    expected_features_df = df_rename_exavg(shifted_df, '_offense', '_defense', t1_cols=t1_cols, t2_cols=t2_cols)

    #### Rename back into home and away features
    home_exavg_features_df = expected_features_df[expected_features_df['is_home'] == 1].copy().drop(columns='is_home')
    away_exavg_features_df = expected_features_df[expected_features_df['is_home'] == 0].copy().drop(columns='is_home')
    home_exavg_features_df.columns = ["home_" + col if 'exavg_' in col or col == 'team' else col for col in home_exavg_features_df.columns]
    away_exavg_features_df.columns = ["away_" + col if 'exavg_' in col or col == 'team' else col for col in away_exavg_features_df.columns]

    #### Merge home and away Expected Average features into base as dataset_df
    dataset_df = pd.merge(base_dataset_df, home_exavg_features_df, on=['home_team', 'season', 'week'], how='left')
    dataset_df = pd.merge(dataset_df, away_exavg_features_df, on=['away_team', 'season', 'week'], how='left')
    dataset_df['game_id'] = dataset_df.apply(lambda x: f"{x['season']}_{x['week']}_{x['away_team']}_{x['home_team']}", axis=1)

    #### Fold base from away and home into team
    folded_dataset_df = base_dataset_df.copy()
    folded_dataset_df['game_id'] = folded_dataset_df.apply(lambda x: f"{x['season']}_{x['week']}_{x['away_team']}_{x['home_team']}", axis=1)
    folded_dataset_df = folded_dataset_df.rename(columns={'spread_line': 'away_spread_line'})
    folded_dataset_df['home_spread_line'] = - folded_dataset_df['away_spread_line']
    folded_dataset_df['home_team_spread'] = -folded_dataset_df['away_team_spread']
    folded_dataset_df['home_team_win'] = folded_dataset_df['away_team_win'] == 0
    folded_dataset_df['home_team_covered_spread'] = folded_dataset_df['away_team_covered_spread'] == 0
    folded_dataset_df = df_rename_fold(folded_dataset_df, 'away_', 'home_')
    folded_dataset_df = pd.merge(folded_dataset_df, expected_features_df, on=['team', 'season', 'week'], how='left')
    dataset_df.index = dataset_df.game_id

    # Customize Column names from feature store into friendly_names
    dataset_df['expected_spread'] = dataset_df['home_exavg_avg_points'] - dataset_df['away_exavg_avg_points']
    dataset_df['expected_total'] = dataset_df['home_exavg_avg_points'] + dataset_df['away_exavg_avg_points']
    dataset_df = dataset_df.rename(columns={
        'away_team_spread': 'actual_away_spread',
        'total_target': 'actual_point_total',
        'away_exavg_avg_points': 'away_expected_points',
        'home_exavg_avg_points': 'home_expected_points',
        'home_elo_pre': 'home_rating',
        'away_elo_pre': 'away_rating',
        'away_score': 'away_actual_points',
        'home_score': 'home_actual_points',
        'away_exavg_avg_carries': 'away_expected_carries',
        'home_exavg_avg_carries': 'home_expected_carries',
        'home_exavg_avg_rushing_yards': 'home_expected_rushing_yards',
        'away_exavg_avg_rushing_yards': 'away_expected_rushing_yards',
        'home_exavg_avg_rushing_tds': 'home_expected_rushing_tds',
        'away_exavg_avg_rushing_tds': 'away_expected_rushing_tds',
        'home_exavg_avg_completions': 'home_expected_completions',
        'away_exavg_avg_completions': 'away_expected_completions',
        'home_exavg_avg_attempts': 'home_expected_attempts',
        'away_exavg_avg_attempts': 'away_expected_attempts',
        'home_exavg_avg_passing_yards': 'home_expected_passing_yards',
        'away_exavg_avg_passing_yards': 'away_expected_passing_yards',
        'home_exavg_avg_passing_tds': 'home_expected_passing_tds',
        'away_exavg_avg_passing_tds': 'away_expected_passing_tds',
        'home_exavg_avg_time_of_possession': 'home_expected_time_of_possession',
        'away_exavg_avg_time_of_possession': 'away_expected_time_of_possession',
        'home_exavg_avg_turnover': 'home_expected_turnover',
        'away_exavg_avg_turnover': 'away_expected_turnover',
        'home_exavg_avg_field_goal_made': 'home_expected_field_goal_made',
        'away_exavg_avg_field_goal_made': 'away_expected_field_goal_made'
    })
    dataset_df['away_rating'] = dataset_df['away_rating'].astype(int)
    dataset_df['home_rating'] = dataset_df['home_rating'].astype(int)

    folded_dataset_df = folded_dataset_df.rename(columns={
        'exavg_avg_points': 'expected_points',
        'exavg_avg_q1_points': 'expected_q1_points',
        'exavg_avg_q2_points': 'expected_q2_points',
        'exavg_avg_q3_points': 'expected_q3_points',
        'exavg_avg_q4_points': 'expected_q4_points',
        'exavg_avg_q5_points': 'expected_q5_points',
        'elo_pre': 'rating',
        'score': 'actual_points',
        'exavg_avg_carries': 'expected_carries',
        'exavg_avg_rushing_yards': 'expected_rushing_yards',
        'exavg_avg_rushing_tds': 'expected_rushing_tds',
        'exavg_avg_completions': 'expected_completions',
        'exavg_avg_attempts': 'expected_attempts',
        'exavg_avg_passing_yards': 'expected_passing_yards',
        'exavg_avg_passing_tds': 'expected_passing_tds',
        'exavg_avg_time_of_possession': 'expected_time_of_possession',
        'exavg_avg_turnover': 'expected_turnover',
        'exavg_avg_field_goal_made': 'expected_field_goal_made'
    })
    folded_dataset_df['rating'] = folded_dataset_df['rating'].astype(int)
    folded_dataset_df['expected_time_of_possession'] = folded_dataset_df['expected_time_of_possession'].apply(lambda x: f"{int(x // 60)}:{int(x % 60):02}")
    return dataset_df, folded_dataset_df

