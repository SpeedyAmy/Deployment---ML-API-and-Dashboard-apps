import streamlit as st
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import openpyxl

### Config
st.set_page_config(
    page_title="Getaround Dashboard Delay Analysis",
    layout="wide"
)

DATA_URL = ('https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_delay_analysis.xlsx')

### App
st.title('Getaround Dashboard')
st.markdown("👋 Hello there! Welcome to this this dashboard that helps analyse checkout delay's impact on Getaround's users")


@st.cache(allow_output_mutation=True)
def load_data(nrows=''):
    data = pd.DataFrame()
    if(nrows == ''):
        data = pd.read_excel("https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_delay_analysis.xlsx")
    else:
        data = pd.read_excel("https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_delay_analysis.xlsx",nrows=nrows)

    return data

st.subheader("LOAD AND SHOWCASE DATA")

data_load_state = st.text('Loading data...')
data = load_data()
data_load_state.text('data_loaded ✔️') # change text from "Loading data..." to "" once the the load_data function has run

## Run the below code if the check is checked ✅
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)    
   

# Late checkouts proportions
### We assume that when a delay is negative it is ot to be considered as delay
st.subheader('LATE CHECKOUT PROPORTION')
st.markdown("""
    You can see the delay distribution here
""")
data['checkout_status']=["Late" if x>0 else "In_time" for x in data.delay_at_checkout_in_minutes]
fig = px.pie(data, names='checkout_status', title='LATE CHECKOUT PROPORTION')
st.plotly_chart(fig)

#plotting checkin_type histogram based on checkin type
st.subheader('CHECKIN TYPE BASED ON CHECKOUT STATUS')
st.markdown("""
    SHowing checkin type based on checkout status
""")
fig = px.histogram(data, x="checkin_type", color="checkout_status", text_auto=True)
fig.show()
st.plotly_chart(fig)

#plotting rental state histogram based on delay or not
st.subheader('RENTAL STATE BASED ON CHECKOUT STATUS')
st.markdown("""
    Showing rental state based on checkout status
""")
fig = px.histogram(data, x="state", color="checkout_status", text_auto=True)
fig.show()
st.plotly_chart(fig)


# Delay at checkout visualization
st.subheader('DELAY DISTRIBUTION')
st.markdown("""Here we will consider the dataset with delays after deleting outliers""")
delay_data=data[data.delay_at_checkout_in_minutes>0]
delay_data = delay_data[
            (delay_data["delay_at_checkout_in_minutes"] <(2*delay_data['delay_at_checkout_in_minutes'].std()))
        ]
fig = px.histogram(delay_data["delay_at_checkout_in_minutes"],x="delay_at_checkout_in_minutes")
fig.update_layout()
st.plotly_chart(fig, use_container_width=True)


# Consecutive rentals : we create a dataset where we keep only rentals that have consecutive rental id non missing values
st.subheader("CONSECUTIVE RENTALS ANALYSIS")
consecutive_rental_data = pd.merge(data, data, how='inner', left_on = 'previous_ended_rental_id', right_on = 'rental_id')

# Keeping columns that caracterise teh rental spcification and potential impact of previous rental
consecutive_rental_data.drop(
    [
        "delay_at_checkout_in_minutes_x",
        "rental_id_y", 
        "car_id_y", 
        "state_y",
        "time_delta_with_previous_rental_in_minutes_y",
        "previous_ended_rental_id_y",
        "checkout_status_x"
    ], 
    axis=1,
    inplace=True
)

consecutive_rental_data.columns = [
    'rental_id',
    'car_id',
    'checkin_type',
    'state',
    'previous_ended_rental_id',
    'time_delta_with_previous_rental_in_minutes',
    'previous_checkin_type',
    'previous_delay_at_checkout_in_minutes',
    "previous_checkout_status"
]

# Remove rows with missing previous rental delay values
consecutive_rental_data = consecutive_rental_data[~consecutive_rental_data["previous_delay_at_checkout_in_minutes"].isnull()]
consecutive_rental_data.reset_index(drop=True, inplace=True)

# Geting checkin delay in MN caused by late checkout with previous rental
consecutive_rental_data['delayed_checkin_in_minutes']=[
    consecutive_rental_data.previous_delay_at_checkout_in_minutes[i]-consecutive_rental_data.time_delta_with_previous_rental_in_minutes[i] for i in range(len(consecutive_rental_data))
    ]
# Assessing cancelled rentals du to delayed checkout with previous rental
cancelled_rentals = consecutive_rental_data[
    (consecutive_rental_data["delayed_checkin_in_minutes"]>0) & (consecutive_rental_data["state"]=="canceled")
    ]
# Assessing impacted rentals du to delayed checkout with previous rental
impacted_rentals= consecutive_rental_data[consecutive_rental_data.delayed_checkin_in_minutes>0]
st.markdown(f"""
    The number of checkins impacted by previous delays is:  **{len(impacted_rentals)}**\n
    The number of potential cancellations due to delays is:  **{len(cancelled_rentals)}**\n
""")

#### Create two columns
col1, col2 = st.columns(2)

with col1:
    
    fig = px.histogram(impacted_rentals,x="delayed_checkin_in_minutes", color="state",title='DELAYED CHECKIN DU TO PREVIOUS LATE CHECKOUT')
    st.plotly_chart(fig)

with col2:
    fig = px.pie(consecutive_rental_data, names='state', title='RENTAL STATUS')
    st.plotly_chart(fig)

# Threshold: minimum time between two rentals to avoid cancellation 
st.subheader("THRESHOLD ANALYSIS")


# Threshold form
with st.form("Threshhold"):
    threshold = st.number_input("Threshold in minutes (with a step à 15mn)", min_value = 0, step = 15)
    checkin_type = st.selectbox("Checkin types", ["Connect only", "Mobile only","All"])
    submit = st.form_submit_button("submit")

    if submit:
        consecutive_rental_data_selected = impacted_rentals
        cancellation_df_selected= cancelled_rentals
        #select checkin type "connect"
        if checkin_type == "Connect only":
            consecutive_rental_data_selected = consecutive_rental_data_selected[consecutive_rental_data_selected["checkin_type"] == "connect"]
            cancellation_df_selected= cancelled_rentals[cancelled_rentals["checkin_type"] == "connect"]
        elif checkin_type == "Mobile only":
            consecutive_rental_data_selected = consecutive_rental_data_selected[consecutive_rental_data_selected["checkin_type"] == "mobile"]
            cancellation_df_selected= cancelled_rentals[cancelled_rentals["checkin_type"] == "mobile"]
        


        avoided_checkin_delays = len(consecutive_rental_data_selected[consecutive_rental_data_selected["delayed_checkin_in_minutes"] < threshold])
            
        avoided_cancellation = len(cancellation_df_selected[cancellation_df_selected["delayed_checkin_in_minutes"] < threshold])

        percentage_avoided_checkin_delays=round((avoided_checkin_delays/len(consecutive_rental_data_selected))*100, 1)
        precentage_avoided_cancellations=round((avoided_cancellation/len(cancellation_df_selected))*100, 1)
        avoided_revenue_loss = round(avoided_cancellation * 121.214536, 2) #I took the average rental_price_per_day provided in pricing dataset

        st.markdown(f"""
            With a threshold of **{threshold}**minutes on **{checkin_type}** there is:
            - **{avoided_checkin_delays}** avoided checkin delays cases ({percentage_avoided_checkin_delays}% solved)
            - **{avoided_cancellation}** avoided cancellations (due to delays) cases ({precentage_avoided_cancellations}% solved)
            - **{avoided_revenue_loss}** avoided revenue loss in $ (due to cancellations and based on average daily rental price) 
        """)

### Side bar 
st.sidebar.header("Getaround dashboards with Streamlit")
st.sidebar.markdown("""
    * [LOAD AND SHOW CASE DATA](#load-and-showcase-data)
    * [LATE CHECKOUT PROPORTION](#late-checkout-proportion)
    * [CHECKIN TYPE BASED ON CHECKOUT STATUS](#checkin-type-based-on-checkout-status)
    * [RENTAL STATE BASED ON CHECKOUT STATUS](#rental-state-based-on-checkout-status)
    * [DELAY DISTRIBUTION](#delay-distribution)
    * [CONSECUTIVE RENTALS ANALYSIS](#consecutive-rentals-analysis)
    * [THRESHOLD ANALYSIS](#threshold-analysis)
""")
e = st.sidebar.empty()
e.write("")
st.sidebar.write("Made with 💖 by [Amina Nasri](https://github.com/SpeedyAmy)")



### Footer 
empty_space, footer = st.columns([1, 2])

with empty_space:
    st.write("")

with footer:
    st.markdown("""
        🍇
        If you want to learn more, check out [my Getaround Repo](https://github.com/SpeedyAmy?tab=repositories) 📖
    """)


