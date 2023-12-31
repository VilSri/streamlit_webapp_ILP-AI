import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from collections import Counter
from zipfile import ZipFile
from st_aggrid import AgGrid, JsCode, GridOptionsBuilder, ColumnsAutoSizeMode
from numerize.numerize import numerize
from calendar import month_name

with ZipFile('Loan Pipeline Pickle.zip', 'r') as zObject:
     pickle_file = zObject.extract('Loan Pipeline.pkl')

loan_pipeline_df = pd.read_pickle(pickle_file)

# Set page configurations
st.set_page_config(
    page_title = 'Intelligent Loan Pipeline Management',
    layout = 'wide',
    initial_sidebar_state = 'expanded'
)

# Define the SessionState class
class SessionState:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

# Function to get the data with caching
@st.cache_data
def get_data():
    return loan_pipeline_df

# Get the data using the caching function
df = get_data()

# Create a SessionState object
session_state = SessionState(
    loan_officer = [],
    loan_processor = [],
    loan_closer = [],
    loan_source = [],
    loan_type = [],
    selected_year = [],
    selected_month = [],
    last_finished_milestone = [],
    selected_min_progress = int(df['Progress'].min()),
    selected_max_progress = int(df['Progress'].max()),
)

header_left, header_mid, header_right = st.columns([1, 2, 1], gap = 'large')

with header_mid:
    st.markdown("<h1 style = 'font-size: 21px; text-align: center; padding-bottom: 5px;'><b>Intelligent Loan Pipeline Management</b></h1>", unsafe_allow_html = True)
st.divider()

# Create the sidebar filters with cached values
with st.sidebar:
    selected_min_progress, selected_max_progress = st.slider(
        label = 'Select Progress',
        value = [session_state.selected_min_progress, session_state.selected_max_progress],
        min_value = int(df['Progress'].min()),
        max_value = int(df['Progress'].max())
    )
    session_state.selected_min_progress = selected_min_progress
    session_state.selected_max_progress = selected_max_progress

    selected_year = st.multiselect(
        label = 'Select Year',
        options = sorted(df["Extracted Year (GFE Application Date)"].unique()),
        default = sorted(df["Extracted Year (GFE Application Date)"].unique()),
    )
    session_state.selected_year = selected_year

    month_lookup = list(month_name)
    selected_month = st.multiselect(
        label = 'Select Month',
        options = sorted(df["Extracted Month (GFE Application Date)"].unique(), key = month_lookup.index),
        default = sorted(df["Extracted Month (GFE Application Date)"].unique(), key = month_lookup.index), 
    )
    session_state.selected_month = selected_month

    loan_officer = st.multiselect(
        label = 'Select Loan Officer',
        options = sorted(df['Loan Officer'].dropna().unique()),
        default = sorted(df['Loan Officer'].dropna().unique()),
    )
    session_state.loan_officer = loan_officer

    loan_processor = st.selectbox(
        label = 'Select Loan Processor',
        options = sorted(df['Loan Processor'].dropna().unique())
        )
    session_state.loan_processor = loan_processor

    loan_closer = st.multiselect(
        label = 'Select Loan Closer',
        options = sorted(df['Loan Closer'].dropna().unique()),
        default = sorted(df['Loan Closer'].dropna().unique()),
    )
    session_state.loan_closer = loan_closer
    
    loan_source = st.multiselect(
        label = 'Select Loan Source',
        options = sorted(df['Loan Source'].dropna().unique()),
        default = sorted(df['Loan Source'].dropna().unique()),
    )
    session_state.loan_source = loan_source

    loan_type = st.multiselect(
        label = 'Select Loan Type',
        options = sorted(df['Loan Type'].dropna().unique()),
        default = sorted(df['Loan Type'].dropna().unique()),
    )
    session_state.loan_type = loan_type

    last_finished_milestone = st.multiselect(
        label = 'Select Last Finished Milestone',
        options = sorted(df['Last Finished Milestone'].dropna().unique()),
        default = sorted(df['Last Finished Milestone'].dropna().unique()),
    )
    session_state.last_finished_milestone = last_finished_milestone

# Apply the filters to the dataframe
filtered_data = df.query('`Extracted Year (Milestone Date - Submittal)` in @selected_year and `Extracted Month (Milestone Date - Submittal)` in @selected_month and `Loan Officer` in @loan_officer and `Loan Processor` in @loan_processor and `Loan Closer` in @loan_closer and `Loan Source` in @loan_source and `Loan Type` in @loan_type and `Last Finished Milestone` in @last_finished_milestone and `Progress` >= @selected_min_progress and `Progress` <= @selected_max_progress')

# Metrics Definition
borrower_intent_to_continue_date = int(filtered_data["GFE Application Date"].count()/2)
uw_submitted = int(filtered_data["GFE Application Date"].count()/3)
uw_cond_approved = int(filtered_data["GFE Application Date"].count()/3.5)
app_approved = int(filtered_data["GFE Application Date"].count()/4)
app_clear_to_close = int(filtered_data["GFE Application Date"].count()/4.5)
app_suspended = int(filtered_data["GFE Application Date"].count()/5)

# Calculate the count of each loan decision within the filtered data
milestone_date_approval = int(filtered_data["Milestone Date - Approval"].count() / 0.1)
milestone_date_submittal = int(filtered_data["Milestone Date - Submittal"].count() / 0.15)
clear_to_close_applications = int(filtered_data["Milestone Date - Clear To Close"].count() / 0.2)
# print(milestone_date_approval)
# print(milestone_date_submittal)
# print(clear_to_close_applications)

# Define the metrics
last_finished_milestone_approval = int(filtered_data["Last Finished Milestone"].eq("Approval").sum())
last_finished_milestone_clear_to_close = int(filtered_data["Last Finished Milestone"].eq("Clear to Close").sum())
last_finished_milestone_completion = int(filtered_data["Last Finished Milestone"].eq("Completion").sum())
last_finished_milestone_cond_approval = int(filtered_data["Last Finished Milestone"].eq("Cond. Approval").sum())
last_finished_milestone_doc_preparation = int(filtered_data["Last Finished Milestone"].eq("Doc Preparation").sum())

total1, total2, total3, total4, total5, total6 = st.columns(6, gap = 'medium')

with total1:
    st.markdown("<style>.metric-label, .metric-value { font-size: 16px !important; }</style>", unsafe_allow_html = True)
    st.image('icons/Borr intend to continue.png', width = 45)
    st.metric(label = "Borr Intent to Con Date", value = numerize(borrower_intent_to_continue_date, decimals = 0))

with total2:
    st.markdown("<style>.metric-label, .metric-value { font-size: 16px !important; }</style>", unsafe_allow_html = True)
    st.image('icons/UW Submitted.png', width = 45)
    st.metric(label = "UW Submitted", value = numerize(uw_submitted, decimals = 0))

with total3:
    st.markdown("<style>.metric-label, .metric-value { font-size: 16px !important; }</style>", unsafe_allow_html = True)
    st.image('icons/UW Cond Approved.png', width = 35)
    st.metric(label = "UW Cond. Approved", value = numerize(uw_cond_approved, decimals = 0))

with total4:
    st.markdown("<style>.metric-label, .metric-value { font-size: 16px !important; }</style>", unsafe_allow_html = True)
    st.image('icons/App Approved.png', width = 45)
    st.metric(label = "Application Approved", value = numerize(app_approved, decimals = 0))

with total5:
    st.markdown("<style>.metric-label, .metric-value { font-size: 16px !important; }</style>", unsafe_allow_html = True)
    st.image('icons/App clear to close.png', width = 45)
    st.metric(label = "Application Clear To Close", value = numerize(app_clear_to_close, decimals = 0))

with total6:
    st.markdown("<style>.metric-label, .metric-value { font-size: 16px !important; }</style>", unsafe_allow_html = True)
    st.image('icons/App suspended.png', width = 45)
    st.metric(label = "Application Suspended", value = numerize(app_suspended, decimals = 0))

# Select and pre-process columns for loan progress table
loan_progress_df = filtered_data[['Loan Type', 'Ageing (days)', 'Loan Number', 'Progress',  'ExpRate Lock', 'ExpAppraisal', 'Exp_Title', 'ExpCredit_Exp', 'Exp_VVOE', 'Exp_HOI', 'Exp_Payoff', 'Exp_Income', 'Borrower Intent to Continue Date']]

# Select and preprocess columns for 'document expiration alerts by loans' table
document_expiration_alerts_df = filtered_data[['Loan Number', 'ExpRate Lock1', 'ExpAppraisal1', 'Exp_Title1', 'ExpCredit_Exp1', 'Exp_HOI1', 'Exp_VVOE1', 'Exp_Income1', 'Exp_Payoff1']]

def get_loan_progress_grid(df, int):
    cellstyle_jscode_loan_progress = JsCode("""
        function(params) {
            var value = params.value;
            if (params.value === 'Closed') {
                return {
                    'color': 'black',
                    'backgroundColor': 'lime'
                };
            }
            if (params.value === 'Pending') {
                return {
                    'color': 'black',
                    'backgroundColor': 'yellow'
                };
            }
            if (value > 0 && value <50) {
                return {
                    'color': 'black',
                    'backgroundColor': 'red'
                };
            }
            if (value >= 50 && value < 100) {
                return {
                    'color': 'black',
                    'backgroundColor': 'yellow'
                };
            }
            if (value == 100) {
                return {
                    'color': 'black',
                    'backgroundColor': 'lime'
                };
            }
            return null;
        }
    """)

    gb_loan_progress = GridOptionsBuilder.from_dataframe(df)
    st.markdown("<h3 style = 'text-align: center; font-size: 25px;'>Loan Progress</h3>", unsafe_allow_html = True)
    gb_loan_progress.configure_default_column(min_column_width = 110, resizable = True, filterable = True, sortable = True, groupable = True)
    gb_loan_progress.configure_column(field = "Loan Type", header_name = "Loan Type", wrapHeaderText = True, autoHeaderHeight = True)
    gb_loan_progress.configure_column(field = "Loan Number", header_name = "Loan Number", wrapHeaderText = True, autoHeaderHeight = True, sort = 'asc')
    gb_loan_progress.configure_column(field = "Ageing (days)", header_name = "Ageing (days)", wrapHeaderText = True, autoHeaderHeight = True)
    gb_loan_progress.configure_column(field = "Progress", header_name = "Progress (%)", cellStyle = cellstyle_jscode_loan_progress, wrapHeaderText = True, autoHeaderHeight = True)
    gb_loan_progress.configure_column(field = "ExpRate Lock", header_name = "Rate Lock (10%)", cellStyle = cellstyle_jscode_loan_progress, wrapHeaderText = True, autoHeaderHeight = True)
    gb_loan_progress.configure_column(field = "ExpAppraisal", header_name = "Appraisal (20%)", cellStyle = cellstyle_jscode_loan_progress, wrapHeaderText = True, autoHeaderHeight = True)
    gb_loan_progress.configure_column(field = "Exp_Title", header_name = "Title (20%)", cellStyle = cellstyle_jscode_loan_progress, wrapHeaderText = True, autoHeaderHeight = True)
    gb_loan_progress.configure_column(field = "ExpCredit_Exp", header_name = "Credit Exp (15%)", cellStyle = cellstyle_jscode_loan_progress, wrapHeaderText = True, autoHeaderHeight = True)
    gb_loan_progress.configure_column(field = "Exp_VVOE", header_name = "VVOE (5%)", cellStyle = cellstyle_jscode_loan_progress, wrapHeaderText = True, autoHeaderHeight = True)
    gb_loan_progress.configure_column(field = "Exp_HOI", header_name = "HOI (5%)", cellStyle = cellstyle_jscode_loan_progress, wrapHeaderText = True, autoHeaderHeight = True)
    gb_loan_progress.configure_column(field = "Exp_Payoff", header_name = "Payoffs (10%)", cellStyle = cellstyle_jscode_loan_progress, wrapHeaderText = True, autoHeaderHeight = True)
    gb_loan_progress.configure_column(field = "Exp_Income", header_name = "Income Exp (15%)", cellStyle = cellstyle_jscode_loan_progress, wrapHeaderText = True, autoHeaderHeight = True)
    gb_loan_progress.configure_column(field = "Borrower Intent to Continue Date", header_name = "Borrower Intent to Continue Date", wrapHeaderText = True, autoHeaderHeight = True)
    grid_options_loan_progress = gb_loan_progress.build()
    loan_progress_table = AgGrid(df, gridOptions = grid_options_loan_progress, columns_auto_size_mode = ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW, fit_columns_on_grid_load = True, height = 400, reload_data = True, allow_unsafe_jscode = True)
    st.markdown("<h6 style = font-size: 5px;'>Closed -- Loan process is completed &emsp; Pending -- Awaits document to be submitted</h6>", unsafe_allow_html = True)
    return loan_progress_table
    
# Tab views
tab1, tab2, tab3 = st.tabs(["Key Metrics", "Loan Pipeline", "AI Assist"])

# Render the tabs
with tab1:
    total1, total2, total3 = st.columns([1,1,2], gap = 'large')
    
    with total1:
        milestone_date_approval_value = [milestone_date_approval, milestone_date_submittal]
        milestone_date_approval_fig = go.Figure(data = [go.Pie(labels = ["Milestone Date Approval", "Milestone Date Submittal"], values = milestone_date_approval_value, hole = 0.7, title = "Milestone Date Approval")])
        milestone_date_approval_fig.update_traces(hoverinfo = 'label+value', textfont_size = 15, marker = dict(colors = ["DodgerBlue", "MediumBlue"]))
        milestone_date_approval_fig.update_layout(showlegend = False)
        st.plotly_chart(milestone_date_approval_fig, use_container_width = True)
        
    with total2:
        clear_to_close_applications_value = [clear_to_close_applications, milestone_date_approval]
        clear_to_close_applications_fig = go.Figure(data = [go.Pie(labels = ["Clear to Close Applications", "Milestone Date Approval"], values = clear_to_close_applications_value, hole = 0.7, title = "Clear to Close Applications (Approval)")])
        clear_to_close_applications_fig.update_traces(hoverinfo = 'label+value', textfont_size = 15, marker = dict(colors = ["DodgerBlue", "MediumBlue"]))
        clear_to_close_applications_fig.update_layout(showlegend = False)
        st.plotly_chart(clear_to_close_applications_fig, use_container_width = True)
        
    with total3:
        last_finished_milestone_fig = go.Figure(go.Bar(x = [last_finished_milestone_doc_preparation, last_finished_milestone_cond_approval, last_finished_milestone_completion, last_finished_milestone_clear_to_close, last_finished_milestone_approval], y = ["Doc Preparation", "Cond. Approval", "Completion", "Clear to Close", "Approval"], orientation = 'h', marker = dict(color = ["DodgerBlue",  "MediumBlue", "DeepSkyBlue", "SlateBlue", "Cyan"]), hoverinfo = 'skip', text = [numerize(last_finished_milestone_doc_preparation, decimals = 0), numerize(last_finished_milestone_cond_approval, decimals = 0), numerize(last_finished_milestone_completion, decimals = 0), numerize(last_finished_milestone_clear_to_close, decimals = 0), numerize(last_finished_milestone_approval, decimals = 0)], textposition = 'inside', width = 0.5))
        last_finished_milestone_fig.update_layout(yaxis = dict(showline = False, showticklabels = True), xaxis = dict(showline = True, showticklabels = True, title = dict(text = "Last Finished Milestone")))
        st.plotly_chart(last_finished_milestone_fig, use_container_width = True)
                    
with tab2:
    global productivity_applications_count_list, average_time_loan_type_list, efficiency_applications_count_list, error_applications_count_list, error_type_list
    
    @st.cache_data
    def get_data_loan_progress():
        return loan_progress_df
    
    # Get the data using the caching function
    frequent_data_loan_progress = get_data_loan_progress()
    
    @st.cache_data()
    def get_data_document_expiration_alerts():
        return document_expiration_alerts_df

    # Get the data using the caching function
    frequent_data_document_expiration_alerts = get_data_document_expiration_alerts()

    with st.container():
        # st.write('AI Insights')
        col1, col2 = st.columns([0.04,1.5], gap = 'small')

        with col1:
            # st.write('')
            st.image('icons/AI3.png', width = 40)

        with col2:
            
            # Filter dataframe for AI suggestion
            suggestion_filter_df = filtered_data[(filtered_data["All Documents Received Status"] == "Yes") & (filtered_data["All Documents Expiration Status"] == "Not Expired") & (filtered_data["Progress"] >= 95)]
            
            productivity_df = suggestion_filter_df[suggestion_filter_df["Expected Time to Complete (minutes)"] <=10]
            
            productivity_total_time_to_complete = int(productivity_df["Expected Time to Complete (minutes)"].sum())
            
            productivity_applications_count_list = []
            if productivity_total_time_to_complete < 100:
                for i in range(len(productivity_df)):
                    productivity_applications_count_list.append(productivity_df.index[i])
            
            efficiency_df = suggestion_filter_df[suggestion_filter_df["Expected Time to Complete (minutes)"] < 15]

            efficiency_applications_count_list = []
            if len(efficiency_df) > 0:
                efficiency_average_time_to_complete = int(efficiency_df["Expected Time to Complete (minutes)"].mean())
                if efficiency_average_time_to_complete <= 10:
                    for i in range(len(efficiency_df)):
                        efficiency_applications_count_list.append(efficiency_df.index[i])
                   
            accuracy_df = suggestion_filter_df[suggestion_filter_df["Error Type"] != "No Error"]

            error_applications_count_list = []
            error_type_list = []
            error_type_unique_list = []
            for i in range(len(accuracy_df)):
                error_applications_count_list.append(accuracy_df.index[i])
                error_type_list.append(accuracy_df.iloc[i, accuracy_df.columns.get_loc("Error Type")])
                if accuracy_df.iloc[i, accuracy_df.columns.get_loc("Error Type")] not in error_type_unique_list:
                    error_type_unique_list.append(accuracy_df.iloc[i, accuracy_df.columns.get_loc("Error Type")])            
            calculate_most_frequent_error_type_list = Counter(error_type_list)
            most_frequent_error_type_list = calculate_most_frequent_error_type_list.most_common()

            most_frequent_error_type_selected_list = []
            if len(most_frequent_error_type_list) > 3:
                for i in range(3):
                    if most_frequent_error_type_list[i][0] not in most_frequent_error_type_selected_list:
                        most_frequent_error_type_selected_list.append(most_frequent_error_type_list[i][0])

            if len(error_applications_count_list) > 0:
                if len(most_frequent_error_type_list) > 3:
                    error_type_string = ", ".join(most_frequent_error_type_selected_list)
                else:
                    error_type_string = ", ".join(error_type_unique_list)

            effectiveness_df = suggestion_filter_df[suggestion_filter_df["Ageing (days)"] < 2]

            effectiveness_applications_count_list = []
            for i in range(len(effectiveness_df)):
                effectiveness_applications_count_list.append(effectiveness_df.index[i]) 
            
            loan_processor_list = []
            for i in range(len(suggestion_filter_df)):
                if suggestion_filter_df.iloc[i, suggestion_filter_df.columns.get_loc("Loan Processor")] not in loan_processor_list:
                    loan_processor_list.append(suggestion_filter_df.iloc[i, suggestion_filter_df.columns.get_loc("Loan Processor")])
            loan_processor_name_list = []
            for i in range(len(loan_processor_list)):
                loan_processor_name_list.append(loan_processor_list[i].split(' ', 1)[0])
            loan_processor_string = ", ".join(loan_processor_name_list)
            st.markdown("<h6 style = 'font-size: 24px; padding-top: 10px; padding-bottom: 10px;'>AI Advisor</h6>", unsafe_allow_html = True)
            if len(productivity_applications_count_list) > 0 or len(efficiency_applications_count_list) > 0 or len(error_applications_count_list) > 0: 
                    st.markdown("<h style = 'font-size: 16px'>Hi! {}, here are your curated queue insights for the day:</h>".format(loan_processor_string), unsafe_allow_html = True)
            # st.write('')
            
            c1, c2 = st.columns([2.8,1], gap = 'small')

            if len(productivity_applications_count_list) > 0 or len(efficiency_applications_count_list) > 0 or len(error_applications_count_list) > 0: 
                if len(productivity_applications_count_list) > 0:
                    with c1:    
                        if len(productivity_applications_count_list) == 1:
                            st.markdown("<h style = 'font-size: 15px'><span style = 'color: DodgerBlue; font-size: 17px'>**Productivity:**</span> **{}** Application in your pipeline is anticipated to complete in total **{}** minutes.</h>".format(len(productivity_applications_count_list), productivity_total_time_to_complete), unsafe_allow_html = True)
                        else:
                            st.markdown("<h style = 'font-size: 15px'><span style = 'color: DodgerBlue; font-size: 17px'>**Productivity:**</span> **{}** Applications in your pipeline are anticipated to complete in total **{}** minutes.</h>".format(len(productivity_applications_count_list), productivity_total_time_to_complete), unsafe_allow_html = True)
                    with c2:
                        # st.markdown("<style>button{height: 5; font-size: 10px; padding-top: 1px !important; padding-bottom: 1px !important;}</style>", unsafe_allow_html=True)
                        st.button(label = "Priortize", key = "productivity", help = "Click here to Priortize Applications for Productivity")
                    # st.write('----')

                if len(efficiency_applications_count_list) > 0:
                    with c1:
                        if len(efficiency_applications_count_list) == 1:
                            st.markdown("<h style = 'font-size: 15px;'><span style = 'color: DodgerBlue; font-size: 17px'>**Efficiency:**</span> **{}** Application with an average closure time of **{}** minutes.</h>".format(len(efficiency_applications_count_list), efficiency_average_time_to_complete), unsafe_allow_html = True)
                        else:
                            st.markdown("<h style = 'font-size: 15px;'><span style = 'color: DodgerBlue; font-size: 17px'>**Efficiency:**</span> **{}** Applications (each) with an average closure time of **{}** minutes.</h>".format(len(efficiency_applications_count_list), efficiency_average_time_to_complete), unsafe_allow_html = True)
                    with c2:
                        # st.markdown("<style>button{height: 5; font-size: 10px; padding-top: 1px !important; padding-bottom: 1px !important;}</style>", unsafe_allow_html=True)
                        st.button(label = "Priortize", key = "efficiency", help = "Click here to Priortize Applications for Efficiency")
                    # st.write('----')

                if len(error_applications_count_list) > 0:
                    with c1:
                        if len(most_frequent_error_type_list) == 1 and len(error_applications_count_list) == 1:
                            st.markdown("<h style = 'font-size: 15px;'><span style = 'color: DodgerBlue; font-size: 17px'>**Accuracy:**:</span> High Likelihood of below error in **{}** Application: <br> &emsp;&emsp;&emsp;&emsp;&nbsp;&nbsp;&nbsp; <span style = 'color: Red'> **{}**</span></h>".format(len(error_applications_count_list), error_type_string), unsafe_allow_html = True)
                        elif len(most_frequent_error_type_list) > 1 and len(most_frequent_error_type_list) <= 3 and len(error_applications_count_list) > 1 and len(error_applications_count_list) <=3:
                            st.markdown("<h style = 'font-size: 15px;'><span style = 'color: DodgerBlue; font-size: 17px'>**Accuracy:**</span> High Likelihood of below errors in **{}** Applications: <br> &emsp;&emsp;&emsp;&emsp;&nbsp;&nbsp;&nbsp; <span style = 'color: Red'> **{}**</span></h>".format(len(error_applications_count_list), error_type_string), unsafe_allow_html = True)
                        else:
                            st.markdown("<h style = 'font-size: 15px;'><span style = 'color: DodgerBlue; font-size: 17px'>**Accuracy:**</span> High Likelihood of below errors in **{}** Applications: <br> &emsp;&emsp;&emsp;&emsp;&nbsp;&nbsp;&nbsp; <span style = 'color: Red'> **{}**</span></h>".format(len(error_applications_count_list), error_type_string), unsafe_allow_html = True)
                    with c2:
                        # st.markdown("<style>button{height: 5; font-size: 10px; padding-top: 1px !important; padding-bottom: 1px !important;}</style>", unsafe_allow_html=True)
                        st.button(label = "Priortize", key = "accuracy", help = "Click here to Priortize Applications for Accuracy")    
                    # st.write('----')

                if len(effectiveness_applications_count_list) > 0:
                    with c1:
                        if len(effectiveness_applications_count_list) == 1:
                            st.markdown("<h style = 'font-size: 15px;'><span style = 'color: DodgerBlue; font-size: 17px'>**Effectiveness:**</span> **{}** Application has high possibility of SLA breach.</h>".format(len(effectiveness_applications_count_list)), unsafe_allow_html = True)
                        else:
                            st.markdown("<h style = 'font-size: 15px;'><span style = 'color: DodgerBlue; font-size: 17px'>**Effectiveness:**</span> **{}** Applications have high possibility of SLA breach.</h>".format(len(effectiveness_applications_count_list)), unsafe_allow_html = True)             
                    with c2:
                        # st.markdown("<style>button{height: 5; font-size: 10px; padding-top: 1px !important; padding-bottom: 1px !important;}</style>", unsafe_allow_html=True)
                        st.button(label = "Priortize", key = "effectiveness", help = "Click here to Priortize Applications for Effectiveness")
                    # st.write('----')            
            else:
                    st.markdown("<h style = 'font-size: 16px;'>Hi! {}, <br>You're doing great. Keep it up!</h>".format(loan_processor_string), unsafe_allow_html = True)
                    
    st.write('----')

    with st.container():
        if st.session_state == '':
            st.session_state = 'False'
        
        if any(st.session_state.values()) == False:
            filtered_data_df = loan_progress_df[loan_progress_df["Progress"].isin(loan_progress_df["Progress"].unique())]
            get_loan_progress_grid(filtered_data_df, 400)            
        else:
            try:
                if st.session_state['productivity']:
                    productivity_priority_df = loan_progress_df[loan_progress_df.index.isin(productivity_applications_count_list)]
                    get_loan_progress_grid(productivity_priority_df, 300)
            except:
                pass
        
            try:
                if st.session_state['efficiency'] == True:
                    efficirncy_priority_df = loan_progress_df[loan_progress_df.index.isin(efficiency_applications_count_list)]
                    get_loan_progress_grid(efficirncy_priority_df, 300)
            except:
                pass
            
            try:
                if st.session_state['accuracy'] == True:
                    accuracy_priority_df = loan_progress_df[loan_progress_df.index.isin(error_applications_count_list)]
                    get_loan_progress_grid(accuracy_priority_df, 300)
            except:
                pass    
            
            try:
                if st.session_state['effectiveness'] == True:
                    effectiveness_priority_df = loan_progress_df[loan_progress_df.index.isin(effectiveness_applications_count_list)]
                    get_loan_progress_grid(effectiveness_priority_df, 300)
            except:
                pass
    
        st.write('---')

    with st.container():
        gb_document_expiration_alerts = GridOptionsBuilder.from_dataframe(frequent_data_document_expiration_alerts)
    
        cellstyle_jscode_document_expiration_alerts = JsCode("""
            function(params) {
                var value = params.value;
                if (params.value === 'Expired') {
                    return {
                        'color': 'black',
                        'backgroundColor': 'red'
                    };
                }
                if (params.value === 'Expiring Soon') {
                    return {
                        'color': 'black',
                        'backgroundColor': 'yellow'
                    };
                }
                if (params.value === 'Not Expired') {
                    return {
                        'color': 'black',
                        'backgroundColor': 'lime'
                    };
                }
                if (params.value === 'Pending') {
                    return {
                        'color': 'black',
                        'backgroundColor': 'lightgray'
                    };
                }
                return null;
            }
        """)

        st.markdown("<h3 style='text-align: center; font-size: 25px'>Document Expiration Alerts by Loans</h3>", unsafe_allow_html = True)
        gb_document_expiration_alerts.configure_default_column(min_column_width = 110, resizable = True, filterable = True, sortable = True, groupable = True)
        gb_document_expiration_alerts.configure_column(field = "Loan Number", header_name = "Loan Number", wrapHeaderText = True, sort = 'asc', autoHeaderHeight = True)
        gb_document_expiration_alerts.configure_column(field = "ExpRate Lock1", header_name = "Rate Lock", cellStyle = cellstyle_jscode_document_expiration_alerts, wrapHeaderText = True, autoHeaderHeight = True)
        gb_document_expiration_alerts.configure_column(field = "ExpAppraisal1", header_name = "Appraisal", cellStyle = cellstyle_jscode_document_expiration_alerts, wrapHeaderText = True, autoHeaderHeight = True)
        gb_document_expiration_alerts.configure_column(field = "Exp_Title1", header_name = "Title", cellStyle = cellstyle_jscode_document_expiration_alerts, wrapHeaderText = True, autoHeaderHeight = True)
        gb_document_expiration_alerts.configure_column(field = "ExpCredit_Exp1", header_name = "Credit", cellStyle = cellstyle_jscode_document_expiration_alerts, wrapHeaderText = True, autoHeaderHeight = True)
        gb_document_expiration_alerts.configure_column(field = "Exp_HOI1", header_name = "HOI", cellStyle = cellstyle_jscode_document_expiration_alerts, wrapHeaderText = True, autoHeaderHeight = True)
        gb_document_expiration_alerts.configure_column(field = "Exp_VVOE1", header_name = "VVOE", cellStyle = cellstyle_jscode_document_expiration_alerts, wrapHeaderText = True, autoHeaderHeight = True)
        gb_document_expiration_alerts.configure_column(field = "Exp_Income1", header_name = "Income", cellStyle = cellstyle_jscode_document_expiration_alerts, wrapHeaderText = True, autoHeaderHeight = True)
        gb_document_expiration_alerts.configure_column(field = "Exp_Payoff1", header_name = "Payoff", cellStyle = cellstyle_jscode_document_expiration_alerts, wrapHeaderText = True, autoHeaderHeight = True)
        grid_options_document_expiration_alerts = gb_document_expiration_alerts.build()
        document_expiration_alerts_table = AgGrid(frequent_data_document_expiration_alerts, gridOptions = grid_options_document_expiration_alerts, columns_auto_size_mode = ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW, fit_columns_on_grid_load = True, height = 400, allow_unsafe_jscode = True)
        st.markdown("<h6 style = font-size: 5px;'>Expired -- Time lapsed to submit the documents</h6>", unsafe_allow_html = True)
        st.markdown("<h6 style = font-size: 5px;'>Expiring Soon -- Time lapse to submit the documents within 10 days</h6>", unsafe_allow_html = True)
        st.markdown("<h6 style = font-size: 5px;'>Not Expired -- Time lapse to submit the document is more than 10 days</h6>", unsafe_allow_html = True)
        st.markdown("<h6 style = font-size: 5px;'>Pending -- Awaits document to be submitted</h6>", unsafe_allow_html = True)

with tab3:
   # Predefined list of questions and corresponding answers
    questions = ["What is the productivity of loan processing over last 3 months?", 
                 "Which type of application having high cycle time?"]
    answers = ["Overall productivity for Apr'23 - 90%,  May'23 - 92%,  Jun'23 - 90%", 
               "FHA loan types processed with 14-17 days on average."]

    # Display the text input and submit button
    user_text = st.text_input("Enter your question:")
    submit_button = st.button("Submit")

    if submit_button:
        if user_text in questions:
            index = questions.index(user_text)
            st.success(answers[index])
        else:
            st.error("Sorry, I don't have an answer to that question.")
