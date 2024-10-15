TARGETS = [
    'actual_home_score',
    'actual_away_score',
    'actual_away_team_win',
    'actual_away_spread',
    'actual_point_total',
    'actual_away_team_covered_spread',
    'actual_under_covered',
]

META = [
    'season',
    'week',
    'home_team',
    'away_team',
]

VEGAS = [
    'spread_line',
    'total_line',
]

ELO = [
    'elo_pre',
    # 'elo_prob',
]

EWMA_FEATURES = [
    'ewma_rushing_offense',
    'ewma_rushing_defense',
    'ewma_passing_offense',
    'ewma_passing_defense',
    'ewma_score_offense',
    'ewma_score_defense',
]

POINT_FEATURES = [
    'avg_points_offense',
    'avg_points_defense',
    'avg_point_differential_offense',
    'avg_point_differential_defense',
    'avg_q1_point_diff_offense',
    'avg_q2_point_diff_offense',
    'avg_q3_point_diff_offense',
    'avg_q4_point_diff_offense',
    'avg_q5_point_diff_offense',
    'avg_q1_points_offense',
    'avg_q2_points_offense',
    'avg_q3_points_offense',
    'avg_q4_points_offense',
    'avg_q5_points_offense',
    'avg_q1_point_diff_defense',
    'avg_q2_point_diff_defense',
    'avg_q3_point_diff_defense',
    'avg_q4_point_diff_defense',
    'avg_q5_point_diff_defense',
    'avg_q1_points_defense',
    'avg_q2_points_defense',
    'avg_q3_points_defense',
    'avg_q4_points_defense',
    'avg_q5_points_defense',
]

ROLLING_COVER_FEATURES = [
    'rolling_spread_cover',
    'rolling_under_cover'
]

DOWN_FEATURES = [
    'avg_first_down_offense',
    'avg_first_down_defense',
    'avg_third_down_converted_offense',
    'avg_third_down_converted_defense',
    'avg_third_down_failed_offense',
    'avg_third_down_failed_defense',
    'avg_fourth_down_converted_offense',
    'avg_fourth_down_converted_defense',
    'avg_fourth_down_failed_offense',
    'avg_fourth_down_failed_defense',
    'avg_third_down_percentage_offense',
    'avg_third_down_percentage_defense',
    'avg_fourth_down_percentage_offense',
    'avg_fourth_down_percentage_defense',
    'avg_first_down_penalty_offense',
    'avg_first_down_penalty_defense',
]

FANTASY_FEATURES = [
    # 'avg_fantasy_points_offense',
    # 'avg_fantasy_points_defense',
    # 'avg_fantasy_points_half_ppr_offense',
    # 'avg_fantasy_points_half_ppr_defense',
    'avg_fantasy_points_ppr_offense',
    'avg_fantasy_points_ppr_defense',
]

COMMON_FEATURES = [
    'avg_total_plays_offense',
    'avg_total_plays_defense',
    'avg_total_yards_offense',
    'avg_total_yards_defense',
    'avg_total_fumbles_offense',
    'avg_total_fumbles_defense',
    'avg_total_fumbles_lost_offense',
    'avg_total_fumbles_lost_defense',
    'avg_total_turnovers_offense',
    'avg_total_turnovers_defense',
    'avg_total_touchdowns_offense',
    'avg_total_touchdowns_defense',
    'avg_total_first_downs_offense',
    'avg_total_first_downs_defense',
    'avg_touchdown_per_play_offense',
    'avg_touchdown_per_play_defense',
    'avg_yards_per_play_offense',
    'avg_yards_per_play_defense',
    'avg_fantasy_point_per_play_offense',
    'avg_fantasy_point_per_play_defense',
    'avg_pass_to_rush_ratio_offense',
    'avg_pass_to_rush_ratio_defense',
    'avg_pass_to_rush_first_down_ratio_offense',
    'avg_pass_to_rush_first_down_ratio_defense',
    'avg_shotgun_offense',
    'avg_shotgun_defense',
    'avg_no_huddle_offense',
    'avg_no_huddle_defense',
    'avg_qb_dropback_offense',
    'avg_qb_dropback_defense',
    'avg_qb_scramble_offense',
    'avg_qb_scramble_defense',
    'avg_goal_to_go_offense',
    'avg_goal_to_go_defense',
    'avg_is_redzone_offense',
    'avg_is_redzone_defense',
    'avg_epa_offense',
    'avg_epa_defense',
    'avg_wpa_offense',
    'avg_wpa_defense',
    'avg_time_of_possession_offense',
    'avg_time_of_possession_defense',
    'avg_turnover_offense',
    'avg_turnover_defense',
]

PENALTY_FEATURES = [
    'avg_offensive_penalty_yards',
    'avg_defensive_penalty_yards',
    'avg_offensive_penalty',
    'avg_defensive_penalty',
]

COMMON_PASSING_FEATURES = [
    'avg_completions_offense',
    'avg_completions_defense',
    'avg_attempts_offense',
    'avg_attempts_defense',
    'avg_passing_yards_offense',
    'avg_passing_yards_defense',
    'avg_passing_tds_offense',
    'avg_passing_tds_defense',
    'avg_interceptions_offense',
    'avg_interceptions_defense',
    'avg_sacks_offense',
    'avg_sacks_defense',
    'avg_sack_yards_offense',
    'avg_sack_yards_defense',
    'avg_sack_fumbles_lost_offense',
    'avg_sack_fumbles_lost_defense',
    'avg_passing_air_yards_offense',
    'avg_passing_air_yards_defense',
    'avg_passing_yards_after_catch_offense',
    'avg_passing_yards_after_catch_defense',
    'avg_passing_first_downs_offense',
    'avg_passing_first_downs_defense',
    'avg_passing_epa_offense',
    'avg_passing_epa_defense',
    'avg_pacr_offense',
    'avg_pacr_defense',
    'avg_dakota_offense',
    'avg_dakota_defense',
    'avg_completion_percentage_offense',
    'avg_completion_percentage_defense',
    'avg_qbr_offense',
    'avg_qbr_defense',
    'avg_yards_per_pass_attempt_offense',
    'avg_yards_per_pass_attempt_defense',
    'avg_sack_rate_offense',
    'avg_sack_rate_defense',

]

COMMON_RUSHING_FEATURES = [
    'avg_carries_offense',
    'avg_carries_defense',
    'avg_rushing_yards_offense',
    'avg_rushing_yards_defense',
    'avg_rushing_tds_offense',
    'avg_rushing_tds_defense',
    'avg_rushing_fumbles_lost_offense',
    'avg_rushing_fumbles_lost_defense',
    'avg_rushing_first_downs_offense',
    'avg_rushing_first_downs_defense',
    'avg_rushing_epa_offense',
    'avg_rushing_epa_defense',
]

RANKING_FEATURES = [
    'elo_pre_rank',
    'avg_points_offense_rank',
    'avg_rushing_yards_offense_rank',
    'avg_passing_yards_offense_rank',
    'avg_total_yards_offense_rank',
    'avg_yards_per_play_offense_rank',
    'avg_total_turnovers_offense_rank',
    'avg_points_defense_rank',
    'avg_rushing_yards_defense_rank',
    'avg_passing_yards_defense_rank',
    'avg_total_yards_defense_rank',
    'avg_yards_per_play_defense_rank',
    'avg_total_turnovers_defense_rank',
    'offensive_rank',
    'defensive_rank',
    'net_rank',
]

KICKING_FEATURES = [
    'avg_field_goal_made_offense',
    'avg_field_goal_made_defense',
    'avg_field_goal_attempt_offense',
    'avg_field_goal_attempt_defense',
    'avg_field_goal_distance_offense',
    'avg_field_goal_distance_defense',
    'avg_extra_point_made_offense',
    'avg_extra_point_made_defense',
    'avg_extra_point_attempt_offense',
    'avg_extra_point_attempt_defense',
    'avg_field_goal_percentage_offense',
    'avg_field_goal_percentage_defense',
    'avg_extra_point_percentage_offense',
    'avg_extra_point_percentage_defense',
]

JUST_SIMPLE_FEATURES = [
    'avg_carries_offense',
    'avg_carries_defense',
    'avg_rushing_yards_offense',
    'avg_rushing_yards_defense',
    'avg_rushing_tds_offense',
    'avg_rushing_tds_defense',
    'avg_completions_offense',
    'avg_completions_defense',
    'avg_attempts_offense',
    'avg_attempts_defense',
    'avg_passing_yards_offense',
    'avg_passing_yards_defense',
    'avg_passing_tds_offense',
    'avg_passing_tds_defense',
    'avg_time_of_possession_offense',
    'avg_time_of_possession_defense',
    'avg_turnover_offense',
    'avg_turnover_defense',
    'avg_field_goal_made_offense',
    'avg_field_goal_made_defense',
]

GLOSSARY = [
    {
        'FEATURE':'expected_points',
        'ENGINEERING': '(Tm. Points For + Opp. Points Against) / 2',
        'DESCRIPTION': 'The mean of the team\'s average points for and the opponents\' average points against up to the given week'
    },
    {
        'FEATURE':'points_over_expected',
        'ENGINEERING': 'mean(Tm. Points For - expected_points)',
        'DESCRIPTION': 'The mean of the difference between the team\'s actual points for and the expected points up to the given week'
    },
    {
        'FEATURE':'team_covered_spread',
        'ENGINEERING': 'sum(Team. Covered Spread)',
        'DESCRIPTION': 'The sum of the covered spreads for the given team up to the given week'
    },
    {
        'FEATURE':'over_covered',
        'ENGINEERING': 'sum((Tm. Points + Opp. Points) > total_line)',
        'DESCRIPTION': 'The sum of the over covered for the given team up to the given week'
    },
    {
        'FEATURE':'offensive_rank',
        'ENGINEERING': 'RANK(mean(RANK(Tm. Points For) + RANK(Tm. Total Yards)))',
        'DESCRIPTION': 'The rank of the mean of the ranks of the team\'s actual points for and the total yards up to the given week'
    },
    {
        'FEATURE':'defensive_rank',
        'ENGINEERING': 'RANK(mean(RANK(Tm. Points Against) + RANK(Opp. Total Yards)))',
        'DESCRIPTION': 'The rank of the mean of the ranks of the team\'s actual points against and the total yards up to the given week'
    },
    {
        'FEATURE':'rating',
        'ENGINEERING': 'TEP Elo Ratings',
        'DESCRIPTION': 'The Elo Rating of the team up to the given week'
    },
    {
        'FEATURE': 'spread_line',
        'ENGINEERING': 'Vegas Line',
        'DESCRIPTION': 'Vegas Point Difference. Lines are always towards the away team (-3 away team favored by 3, +3 away team under dog)'
    },
    {
        'FEATURE': 'total_line',
        'ENGINEERING': 'Vegas Point Total',
        'DESCRIPTION': 'Vegas Point Total. '
    },
]
