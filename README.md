

## Overview

MyChampion is a Streamlit-based web application designed to help players find their next League of Legends champion based on customizable preferences. The tool uses champion statistics and user-selected filters to generate personalized champion recommendations.

## Features

- Recommend champions based on numeric stats such as attack damage, attack speed, armor, etc
- Filter recommendations by role/position (Top, Jungle, Mid, ADC, Support)
- Support for categorical attributes such as resource type and primary role
- Option to ignore specific attributes to broaden or narrow recommendations
- Ranged and melee selection 
- Clean Streamlit interface

## How It Works

1. Loads and processes champion data
2. Encodes categorical features using label encoding
3. Normalizes numeric features using standard scaling
4. Builds a user preference vector
5. Computes weighted distance between user preferences and champions
6. Returns the closest matching champions

## Packages
- Streamlit
- Pandas
- NumPy
- Scikit-learn

## Project Structure

- MyChampion.py: Main app
- lol_champion_dataset.csv: Dataset file

## Installation

pip install streamlit pandas numpy scikit-learn

Run:

streamlit run MyChampion.py


