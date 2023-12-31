import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

pd.set_option("styler.render.max_elements", 61557285)

st.set_page_config(page_title="Vahan Dashboard!!!", page_icon=":bar_chart:",layout="wide")

st.title(" :bar_chart: Vahan 4 EDA")

st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)
fl = st.file_uploader(":file_folder: Upload a file",type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename, encoding = "ISO-8859-1")
else:
    os.chdir(r"c:\Users\dell\OneDrive - AlmaBetter\Desktop\dash")
    df = pd.read_csv("Final_Registration_Data.csv", encoding = "ISO-8859-1")

col1, col2 = st.columns((2))
df["regn_date"] = pd.to_datetime(df["regn_date"])

# Getting the min and max date 
startDate = pd.to_datetime(df["regn_date"]).min()
endDate = pd.to_datetime(df["regn_date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["regn_date"] >= date1) & (df["regn_date"] <= date2)].copy()

st.sidebar.header("Choose your filter: ")
# Create for Region
fuel = st.sidebar.multiselect("Pick the Fuel Type", df["Fuel_name"].unique())
if not fuel:
    df2 = df.copy()
else:
    df2 = df[df["Fuel_name"].isin(fuel)]

# Create for State
state = st.sidebar.multiselect("Pick the State", df2["State_Name"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State_Name"].isin(state)]

# Create for City
rto = st.sidebar.multiselect("Pick the RTO",df3["off_name"].unique())

# Filter the data based on Region, State and City

if not fuel and not state and not rto:
    filtered_df = df
elif not state and not rto:
    filtered_df = df[df["Fuel_name"].isin(fuel)]
elif not fuel and not rto:
    filtered_df = df[df["State"].isin(state)]
elif state and rto:
    filtered_df = df3[df["State"].isin(state) & df3["off_name"].isin(rto)]
elif fuel and rto:
    filtered_df = df3[df["Fuel_name"].isin(fuel) & df3["off_name"].isin(rto)]
elif fuel and state:
    filtered_df = df3[df["Fuel_name"].isin(fuel) & df3["State"].isin(state)]
elif rto:
    filtered_df = df3[df3["off_name"].isin(rto)]
else:
    filtered_df = df3[df3["Fuel_name"].isin(fuel) & df3["State"].isin(state) & df3["off_name"].isin(rto)]

category_df = filtered_df.groupby(by = ["vehicle_category"], as_index = False)["total"].sum()

with col1:
    st.subheader("Category wise Total Registration ")
    fig = px.bar(category_df, x = "vehicle_category", y = "total", text = ['${:,.2f}'.format(x) for x in category_df["total"]],
                 template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)

with col2:
    st.subheader("Fuel wise Total Registration")
    fig = px.pie(filtered_df, values = "total", names = "Fuel_name", hole = 0.5)
    fig.update_traces(text = filtered_df["Fuel_name"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)

cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Category.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')

with cl2:
    with st.expander("Fuel_name_ViewData"):
        fuel = filtered_df.groupby(by = "Fuel_name", as_index = False)["total"].sum()
        st.write(fuel.style.background_gradient(cmap="Oranges"))
        csv = fuel.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Fuel_name.csv", mime = "text/csv",
                        help = 'Click here to download the data as a CSV file')
        
filtered_df["month_year"] = filtered_df["regn_date"].dt.to_period("M")
st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["total"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y="total", labels = {"total": "Registration"},height=500, width = 1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data = csv, file_name = "TimeSeries.csv", mime ='text/csv')

# Create a treem based on Region, category, sub-Category
st.subheader("Hierarchical view of total registered vehicle  using TreeMap")
fig3 = px.treemap(filtered_df, path = ["Fuel_name","vehicle_category"], values = "total",hover_data = ["total"],
                  color = "Fuel_name")
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader('Norms_Name wise total')
    fig = px.pie(filtered_df, values = "total", names = "Norms_Name", template = "plotly_dark")
    fig.update_traces(text = filtered_df["Norms_Name"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

with chart2:
    st.subheader('Category wise total')
    fig = px.pie(filtered_df, values = "total", names = "vehicle_category", template = "gridon")
    fig.update_traces(text = filtered_df["vehicle_category"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

import plotly.figure_factory as ff
st.subheader(":point_right: Month wise Maker_Name total Summary")
with st.expander("Summary_Table"):
    df_sample = df[0:5][["Fuel_name","State_Name","off_name","Maker_Name","Norms_Name","vehicle_category","vh_class","total"]]
    fig = ff.create_table(df_sample, colorscale = "Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month wise Maker_Name Table")
    filtered_df["month"] = filtered_df["regn_date"].dt.month_name()
    Maker_Name_Year = pd.pivot_table(data = filtered_df, values = "total", index = ["Maker_Name"],columns = "month")
    st.write(Maker_Name_Year.style.background_gradient(cmap="Blues"))

# Create a scatter plot
data1 = px.scatter(filtered_df, x = "Maker_Name", y = "total", size = "owner_code")
data1['layout'].update(title="Relationship between Sales and Profits using Scatter Plot.",
                       titlefont = dict(size=20),xaxis = dict(title="Maker_Name",titlefont=dict(size=19)),
                       yaxis = dict(title = "total", titlefont = dict(size=19)))
st.plotly_chart(data1,use_container_width=True)

#st.write(df.head(10).style.background_gradient(cmap="Oranges"))

with st.expander("View Data"):
    st.write(filtered_df.head().style.background_gradient(cmap="Oranges"))
"""
# Download orginal DataSet
csv = df.to_csv(index = False).encode('utf-8')
st.download_button('Download Data', data = csv, file_name = "Data.csv",mime = "text/csv")


csv_string = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button('Download Data', data=csv_string, file_name="filtered_data.csv", mime="text/csv")

"""