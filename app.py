import streamlit as st
import numpy as np
import pandas as pd
import plotly.figure_factory as ff 
import datetime


st.title("Hello Streamlit 🚀")
st.write("Streamlit berhasil jalan di Python 3.10!")


st.markdown("*Streamlit* is **really** ***cool***.")
st.markdown('''
    :red[Streamlit] :orange[can] :green[write] :blue[text] :violet[in]
    :gray[pretty] :rainbow[colors] and :blue-background[highlight] text.''')
st.markdown("Here's a bouquet &mdash;\
            :tulip::cherry_blossom::rose::hibiscus::sunflower::blossom:")

multi = '''If you end a line with two spaces,
a soft return is used for the next line.

Two (or more) newline characters in a row will result in a hard return.
'''
st.markdown(multi)


st.title("Dashboard Suhu 🌡️")

# Metric sederhana
st.metric(label="Suhu Ruangan", value="25°C")

##### SUHU 
import streamlit as st

st.title("Dashboard Suhu 🌡️")

# Misal data hari ini & kemarin
suhu_hari_ini = 25
suhu_kemarin = 23

# Hitung delta
delta_suhu = suhu_hari_ini - suhu_kemarin
delta_text = f"{delta_suhu}°C"

# Kalau naik, tambahkan panah
if delta_suhu > 0:
    delta_text += " ↑"
elif delta_suhu < 0:
    delta_text += " ↓"

# Tampilkan metric
st.metric(label="Suhu Ruangan", value=f"{suhu_hari_ini}°C", delta=delta_text)


#####  CHARTS #######

chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])

st.area_chart(chart_data)

st.bar_chart(chart_data)

st.line_chart(chart_data)

#### PLOTLY ######
# Add histogram data
x1 = np.random.randn(200) - 2
x2 = np.random.randn(200)
x3 = np.random.randn(200) + 2

# Group data together
hist_data = [x1, x2, x3]

group_labels = ['Group 1', 'Group 2', 'Group 3']

# Create distplot with custom bin_size
fig = ff.create_distplot(
        hist_data, group_labels, bin_size=[.1, .25, .5])

# Plot!
st.plotly_chart(fig, use_container_width=True)


#### TOMBOL ###
st.button("Reset", type="primary")
if st.button("Say hello"):
    st.write("Why hello there")
else:
    st.write("Goodbye")

if st.button("Aloha", type="tertiary"):
    st.write("Ciao")


agree = st.checkbox("I agree")

if agree:
    st.write("Great!")


options = st.multiselect(
    "What are your favorite colors",
    ["Green", "Yellow", "Red", "Blue"],
    ["Yellow", "Red"],
)

st.write("You selected:", options)


### LINER ###

start_color, end_color = st.select_slider(
    "Select a range of color wavelength",
    options=[
        "red",
        "orange",
        "yellow",
        "green",
        "blue",
        "indigo",
        "violet",
    ],
    value=("red", "blue"),
)
st.write("You selected wavelengths between", start_color, "and", end_color)


on = st.toggle("Activate feature")

if on:
    st.write("Feature activated!")

values = st.slider("Select a range of values", 0.0, 100.0, (25.0, 75.0))
st.write("Values:", values)


#### INPUT BOX ###
number = st.number_input(
    "Insert a number", value=None, placeholder="Type a number..."
)
st.write("The current number is ", number)


d = st.date_input("When's your birthday", datetime.date(2019, 7, 6))
st.write("Your birthday is:", d)


### IMAGES LOCAL / LINK ###
import streamlit as st
# st.image("/Users/bqdesy/streamlit_project/images/DSC05557.JPG", caption="Sunrise by the mountains")


col1, col2, col3 = st.columns(3)

with col1:
    st.header("A cat")
    st.image("https://static.streamlit.io/examples/cat.jpg")

with col2:
    st.header("A dog")
    st.image("https://static.streamlit.io/examples/dog.jpg")

with col3:
    st.header("An owl")
    st.image("https://static.streamlit.io/examples/owl.jpg")

