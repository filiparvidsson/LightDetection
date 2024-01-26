import streamlit as st
import datetime as dt
import pandas as pd
import pymongo

def init_connection():
   return pymongo.MongoClient(st.secrets["mongo"]["connection_url"])

client = init_connection()

def get_data():
    db = client.Pico # Database name
    items = db.Logbook.find()
    items = list(items)
    return items

def post_data(title, body, time):
    db = client.Pico # Database name
    db.Logbook.insert_one({"title": title, "body": body, "time": time.strftime("%Y-%m-%d %H:%M")})

data = get_data()

st.title("Logbook")
st.sidebar.title("Create New Entry")
title = st.sidebar.text_input("Entry Title")
body = st.sidebar.text_area("Entry Body")
if st.sidebar.button("Add Entry"):
    post_data(title, body, dt.datetime.utcnow())
    data.append({"title": title, "body": body, "time": dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M")})
    st.sidebar.success("Entry Added")
    

# Print results.
for item in data:
    st.write(item["time"])
    st.write(item["title"])
    st.write(item["body"])
    st.write("----")
