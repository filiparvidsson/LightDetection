import streamlit as st
import pymongo
import pandas as pd
import os

@st.cache_resource
def init_connection():
   return pymongo.MongoClient(st.secrets["mongo"]["connection_url"])

client = init_connection()

@st.cache_data(ttl=60)
def get_data():
    db = client.Pico # Database name
    items = db.LDR2024.find()
    items = list(items)
    return items

def sum_data(data):
    # count number of indexes which has value under 200
    count_light = 0
    count_dark = 0

    for item in data:
        if item["value"] < 200:
            count_light += 1
        else:
            count_dark += 1
    
    return count_light, count_dark

data = get_data()
# visualize the data using the "value" and "timeStamp", the timeStamp is a UTC timestamp
df = pd.DataFrame(data)
df = df.set_index("timeStamp")
df = df.sort_index()

# visualize using streamlit line chart
st.title("Vizualisation")
st.line_chart(df["value"], color="#0868ac")

if st.button("Click here to download"):
    st.sidebar.success("Entries Downloaded")
    # if the entries csv already exists, delete it
    try:
        os.remove("entries.csv")
    except:
        pass
    df.to_csv("entries.csv", index=False)
    st.download_button(
        label="Download Entries",
        data=df.to_csv().encode("utf-8"),
        file_name="entries.csv",
        mime="text/csv",
    )

st.title("Room brightness")
st.line_chart(1400 - df["value"], color="#7bccc4")

st.title("Light on vs Light off")
count_light, count_dark = sum_data(data)
st.write("On: ", count_light, "minutes")
st.write("Off: ", count_dark, "minutes")


