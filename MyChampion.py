import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler


# -------------------------
# DATA
# -------------------------
@st.cache_data
def load_data():
    return pd.read_csv("lol_champion_dataset.csv")


df_raw = load_data()


# -------------------------
# FEATURES
# -------------------------
NUMERIC_FEATURES = [
    "attackdamage", "attackdamageperlevel", "attackspeed", "attackspeedperlevel",
    "crit", "critperlevel", "armor", "armorperlevel", "spellblock", "spellblockperlevel",
    "hp", "hpperlevel", "movespeed", "hpregen", "hpregenperlevel",
    "mpregen", "mpregenperlevel", "mp", "mpperlevel", "attackrange",
    "info_attack", "info_defense", "info_magic", "info_difficulty"
]

FEATURE_LABELS = {
    "attackdamage": "Attack Damage",
    "attackdamageperlevel": "Attack Growth",
    "attackspeed": "Attack Speed",
    "crit": "Crit",
    "armor": "Armor",
    "spellblock": "Magic Resistance",
    "hp": "HP",
    "movespeed": "Move Speed",
    "attackrange": "Range",
    "info_attack": "Atk",
    "info_defense": "Def",
    "info_magic": "Magic",
    "info_difficulty": "Difficulty",
    'hpperlevel':'HP Per Level',
    'hpregen':'HP Regen',
    'hpregenperlevel':'HP Regen Per Level',
    'mpregen':'Mana Regen',
    'mpregenperlevel':"Mana Regen Per Level",
    'mp':'Magic Power',
    'mpperlevel':'Magic Power Per Level'
}

CAT_FEATURES = ["primary_role", "resource_type"]


# -------------------------
# POSITION MAP (single dropdown)
# -------------------------
position_map = {
    "Bottom": 0,
    "Jungle": 1,
    "Middle": 2,
    "Support": 3,
    "Top": 4
}


# -------------------------
# MODEL PREP
# -------------------------
model_df = df_raw[
    ["champion_name", "positions"] + NUMERIC_FEATURES + CAT_FEATURES
].copy()

label_encoders = {}

for col in CAT_FEATURES:
    le = LabelEncoder()
    model_df[col] = le.fit_transform(model_df[col].astype(str))
    label_encoders[col] = le

model_df["position"] = df_raw["positions"].map(position_map)
model_df["is_ranged"] = df_raw["is_ranged"].astype(int)

scaler = StandardScaler()
model_df[NUMERIC_FEATURES] = scaler.fit_transform(model_df[NUMERIC_FEATURES])

ALL_FEAT = NUMERIC_FEATURES + ["position"] + CAT_FEATURES + ["is_ranged"]

X = model_df[ALL_FEAT].values
champion_names = model_df["champion_name"].values
champion_positions = model_df["positions"].values


# -------------------------
# RECOMMENDER
# -------------------------
def recommend_champions(user_numeric, user_position, user_categorical,
                        user_ranged,
                        ignore_numeric, ignore_position,
                        ignore_categorical, ignore_ranged,
                        top_n=10):

    user_num_scaled = scaler.transform([user_numeric])[0]

    user_cat_encoded = []
    for col in CAT_FEATURES:
        raw_val = user_categorical[col]
        le = label_encoders[col]

        if raw_val == "All":
            encoded = 0
        elif raw_val in le.classes_:
            encoded = le.transform([raw_val])[0]
        else:
            encoded = 0

        user_cat_encoded.append(encoded)

    user_vec = np.concatenate([
        user_num_scaled,
        np.array([user_position], dtype=float),
        np.array(user_cat_encoded, dtype=float),
        np.array([user_ranged], dtype=float)
    ])

    weights = np.ones(len(ALL_FEAT))

    # numeric weights
    weights[:len(NUMERIC_FEATURES)] = [0 if x else 1 for x in ignore_numeric]

    # position weight
    pos_idx = len(NUMERIC_FEATURES)
    weights[pos_idx] = 0 if ignore_position else 1

    # categorical weights
    cat_start = len(NUMERIC_FEATURES) + 1
    weights[cat_start:cat_start + len(CAT_FEATURES)] = [
        0 if x else 1 for x in ignore_categorical
    ]

    # ranged weight
    weights[-1] = 0 if ignore_ranged else 1

    diff = X - user_vec
    distances = np.sqrt((weights * diff ** 2).sum(axis=1))

    top_idx = np.argsort(distances)[:top_n]

    return [
        (champion_names[i], champion_positions[i])
        for i in top_idx
    ]


# -------------------------
# UI
# -------------------------
st.set_page_config(page_title="MyChampion", layout="wide")
st.header("MyChampion",text_alignment="center")    
st.sidebar.header("Preferences",text_alignment="center")


# -------------------------
# NUMERIC (SIDE IGNORE FIX)
# -------------------------
st.sidebar.subheader("Numeric Stats")

user_numeric = []
ignore_numeric = []

for feat in NUMERIC_FEATURES:
    min_val = float(df_raw[feat].min())
    max_val = float(df_raw[feat].max())

    if min_val == max_val:
        user_numeric.append(min_val)
        ignore_numeric.append(True)
        continue

    step = max((max_val - min_val) / 50.0, 1e-6)

    col1, col2 = st.sidebar.columns([4, 1])

    with col1:
        val = st.slider(
            label=FEATURE_LABELS.get(feat, feat),
            min_value=min_val,
            max_value=max_val,
            value=(min_val + max_val) / 2.0,
            step=step,
            key=f"slider_{feat}"
        )

    with col2:
        ignore = st.checkbox(
            "Ignore",
            key=f"ignore_{feat}",
        )

    user_numeric.append(val)
    ignore_numeric.append(ignore)


# -------------------------
# POSITION
# -------------------------
st.sidebar.subheader("Position")

position_choice = st.sidebar.selectbox(
    "Role",
    ["All", "Bottom", "Jungle", "Middle", "Support", "Top"],
    index=0
)

ignore_position = (position_choice == "All")
user_position = 0 if ignore_position else position_map[position_choice]


# -------------------------
# CATEGORICAL
# -------------------------
st.sidebar.subheader("Categorical Stats")

user_categorical = {}
ignore_categorical = []

for feat in CAT_FEATURES:
    options = list(label_encoders[feat].classes_) + ["All"]

    col1, col2 = st.sidebar.columns([4, 1])

    with col1:
        val = st.sidebar.selectbox(
            feat,
            options,
            index=len(options) - 1,
            key=f"cat_{feat}"
        )

    with col2:
        ignore = st.sidebar.checkbox(
            "Ignore",
            key=f"ignore_cat_{feat}"
        )

    user_categorical[feat] = val
    ignore_categorical.append(ignore)


# -------------------------
# RANGED / MELEE
# -------------------------
st.sidebar.subheader("Attack Type")
ignore_ranged=[]

ranged_choice = st.sidebar.selectbox(
    "Type",
    ["All", "Ranged", "Melee"],
    index=0
)

user_ranged = 1 if ranged_choice == "Ranged" else 0


# -------------------------
# RUN
# -------------------------
if st.sidebar.button("Get Recommendations", type="primary"):
    with st.spinner("Finding champions..."):
        recommendations = recommend_champions(
            np.array(user_numeric, dtype=float),
            user_position,
            user_categorical,
            user_ranged,
            ignore_numeric,
            ignore_position,
            ignore_categorical,
            ignore_ranged,
            top_n=10
        )

    st.success("Top 10 Champions")

    df = pd.DataFrame(recommendations,
                   columns=["Champion", "Positions"])

    df.insert(0, "Rank", range(1, len(df) + 1))

    st.dataframe(df, use_container_width=True)

else:
    st.info("Adjust settings and click Get Recommendations.")