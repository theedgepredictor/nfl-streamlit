STYLE = """
    <style>
        .stTabs [data-baseweb="tab-list"] {
            justify-content: center;
            text-align: center;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding-top: 10px;
            padding-bottom: 10px;
            padding-left: 20px;
            padding-right: 20px;
            margin: 0 5px;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #f0f0f0;
        }
    </style>
    <style>
        div[data-baseweb="tab-panel"] {
            justify-content: center;
            text-align: center;
        }
        div[class="plot-container plotly"] {
            justify-content: center;
            text-align: center;
        }
        div[data-testid="column"] {
            text-align: center;
        }
        div[data-testid="column"]:nth-of-type(1) {
            justify-content: left;
            padding-left: 20px;
        }
        div[data-testid="column"]:nth-of-type(2) {
            justify-content: center;
            text-align: center;
        }
        div[data-testid="column"]:nth-of-type(3) {
            justify-content: right;
            padding-right: 20px;
        }
        div[data-testid="stSelectbox"] {
            display: block;
            text-align: center;
            padding-right: 25%;
            padding-left: 25%
        }
        p {
            padding-bottom: 0px;
        }
    </style>
"""