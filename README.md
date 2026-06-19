# MyChampon
# A Streamlit made website to help people find their next LOL Champion

## Overview
My Champion uses numerical champion data such as attack damage, armor,
and magic resistance, as well as categorical champion data,
such as the champion's most popular position or their fighter type
to help you find a new champion to play based on your play style

## How to Use this App
Go to https://mychampion.streamlit.app
Input all the different data based on your playstyle
(If there's a metric that you don't really care about, 
you can check the ignore box to ignore that metric)

## Tweaking
# If you want to make something like this for a different game
1. Download the zip file
2.  extract the contents
3.  open your IDE
4.  run
  ```bash
pip install -r requirements.txt
```
5. Open the code and tweak the Categorical and Numerical Features to what matches your dataset
6. If you want custom labels on your website that differ from the dataset columns, just add the column name: your name to the featured labels dictionary.
7. To build run
```bash
streamlit run MyChampion.py
```
and you should have your own website
