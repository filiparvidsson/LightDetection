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

data = get_data()
# visualize the data using the "value" and "timeStamp", the timeStamp is a UTC timestamp
df = pd.DataFrame(data)
df = df.set_index("timeStamp")
df = df.sort_index()

# visualize using streamlit line chart with a slider to select the date range
st.title("Vizualisation")
st.line_chart(df["value"])

if st.button("Download Entries"):
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

