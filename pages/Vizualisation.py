import streamlit as st
import pymongo
import pandas as pd
import os
import config

@st.cache_resource
def init_connection():
   return pymongo.MongoClient(st.secrets["mongo"]["connection_url"])

client = init_connection()

@st.cache_data(ttl=config.CACHE_TTL)
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
        if item["value"] < config.LIGHT_THRESHOLD:
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
        os.remove(config.CSV_FILE)
    except:
        pass
    df.to_csv(config.CSV_FILE, index=False)
    st.download_button(
        label="Download Entries",
        data=df.to_csv().encode("utf-8"),
        file_name=config.CSV_FILE,
        mime="text/csv",
    )

st.title("Room brightness")
# calculate the median with a rolling window of 10 minutes
df["median_diff"] = config.START_VALUE - df["value"].rolling(center=True, window=config.MEDIAN_WINDOW).median()
# calculate the medium
df["mean_diff"] = config.START_VALUE - df["value"].rolling(center=True, window=config.MEAN_WINDOW).mean()
# calculate the difference
df["diff"] = config.START_VALUE - df["value"]
# display the two lines
st.line_chart(df[["diff", "mean_diff", "median_diff"]], color=["#d9f0a3", "#41ab5d", "#006837"])


st.title("Light on vs Light off")
count_light, count_dark = sum_data(data)
st.write("On: ", count_light, "minutes")
st.write("Off: ", count_dark, "minutes")


