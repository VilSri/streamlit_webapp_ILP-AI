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

    loan_processor = st.multiselect(
        label = 'Select Loan Processor',
        options = sorted(df['Loan Processor'].dropna().unique()),
        default = sorted(df['Loan Processor'].dropna().unique()),
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

# filtered_data_grid = df.query('`Loan Processor` in @loan_processor and `Loan Type` in @loan_type')

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
    st.markdown("<style>.metric-label, .metric-value { font-size: 5px !important; }</style>", unsafe_allow_html = True)
    st.image('icons/Borr intend to continue.png', width = 45)
    st.metric(label = "Borr Intent to Con Date", value = numerize(borrower_intent_to_continue_date, decimals = 0))

with total2:
    st.markdown("<style>.metric-label, .metric-value { font-size: 14px !important; }</style>", unsafe_allow_html = True)
    st.image('icons/UW Submitted.png', width = 45)
    st.metric(label = "UW Submitted", value = numerize(uw_submitted, decimals = 0))

with total3:
    st.markdown("<style>.metric-label, .metric-value { font-size: 14px !important; }</style>", unsafe_allow_html = True)
    st.image('icons/UW Cond Approved.png', width = 35)
    st.metric(label = "UW Cond. Approved", value = numerize(uw_cond_approved, decimals = 0))

with total4:
    st.markdown("<style>.metric-label, .metric-value { font-size: 14px !important; }</style>", unsafe_allow_html = True)
    st.image('icons/App Approved.png', width = 45)
    st.metric(label = "Application Approved", value = numerize(app_approved, decimals = 0))

with total5:
    st.markdown("<style>.metric-label, .metric-value { font-size: 14px !important; }</style>", unsafe_allow_html = True)
    st.image('icons/App clear to close.png', width = 45)
    st.metric(label = "Application Clear To Close", value = numerize(app_clear_to_close, decimals = 0))

with total6:
    st.markdown("<style>.metric-label, .metric-value { font-size: 10px !important; }</style>", unsafe_allow_html = True)
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
    # st.markdown("<h3 style = 'text-align: center; font-size: 25px; padding-top: 45px;'>Loan Progress</h3>", unsafe_allow_html = True)
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
    # st.markdown("<h6 style = font-size: 5px;'>Closed -- Loan process is completed &emsp; Pending -- Awaits document to be submitted</h6>", unsafe_allow_html = True)
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
    
    # @st.cache_data
    # def get_data():
    #     return filtered_data
    @st.cache_data
    def get_data_loan_progress():
        return loan_progress_df
    
    # Get the data using the caching function
    frequent_data_loan_progress = get_data_loan_progress()

    # gb_loan_progress = GridOptionsBuilder.from_dataframe(frequent_data_loan_progress)
        
    @st.cache_data()
    def get_data_document_expiration_alerts():
        return document_expiration_alerts_df

    # Get the data using the caching function
    frequent_data_document_expiration_alerts = get_data_document_expiration_alerts()

    # st.write('AI Suggestions')
    # st.markdown("<h6 style = 'text-align: center; font-size: 25px; padding-top: 15px;'>AI Suggestions</h6>", unsafe_allow_html = True)
    with st.container():
        # st.write('AI Insights')
        col1, col2 = st.columns([0.5,3], gap = 'large')

        # st.markdown("<span style='color:lightgreen'>AI Insights</span>", unsafe_allow_html=True)
        
        # st.markdown()

        with col1:
            st.write('')
            st.image('icons/AI1.png', use_column_width = True)

        
        with col2:
            st.markdown("<h6 style = 'font-size: 18px; padding-top: 10px; padding-bottom: 0px;'>AI Suggestions</h6>", unsafe_allow_html = True)
            st.write('')
            
            # Filter dataframe for AI suggestion
            suggestion_filter_df = filtered_data[(filtered_data["All Documents Received Status"] == "Yes") & (filtered_data["All Documents Expiration Status"] == "Not Expired") & (filtered_data["Progress"] >= 95)]
            # (filtered_data["Progress"].isin(filtered_data["Progress"].unique()))

            productivity_df = suggestion_filter_df[suggestion_filter_df["Expected Time to Complete (minutes)"] < 15]
            # productivity_average_time_to_complete = int(suggestion_filter_df["Expected Time to Complete (minutes)"].mean())
            productivity_total_time_to_complete = int(productivity_df["Expected Time to Complete (minutes)"].sum())
            # productivity_total_applications = suggestion_filter_df["Expected Time to Complete (minutes)"].count()

            productivity_applications_count_list = []
            if productivity_total_time_to_complete:
                for i in range(len(productivity_df)):
                    productivity_applications_count_list.append(productivity_df.index[i])
                    # productivity_applications_count_list.append(suggestion_filter_df["Loan Number"][i])
            
            efficiency_df = suggestion_filter_df[suggestion_filter_df["Expected Time to Complete (minutes)"] < 15]

            efficiency_applications_count_list = []
            if len(efficiency_df) > 0:
                efficiency_average_time_to_complete = int(efficiency_df["Expected Time to Complete (minutes)"].mean())
                if efficiency_average_time_to_complete < 11:
                    for i in range(len(efficiency_df)):
                        efficiency_applications_count_list.append(efficiency_df.index[i])
                    # for j in range(len(average_time_loan_type_list)):
                    #     if suggestion_filter_df.iloc[i, suggestion_filter_df.columns.get_loc("Loan Type")] ==                 average_time_loan_type_list[j]:
                    #         efficiency_applications_count_list.append(suggestion_filter_df.index[i])


            # efficiency_total_time_to_complete = int(efficiency_df["Expected Time to Complete (minutes)"].sum())
            # efficiency_total_applications = efficiency_df["Expected Time to Complete (minutes)"].count()

            # average_time_taken_groupby = suggestion_filter_df.groupby("Loan Type", as_index = False)
            # average_time_loan_type = average_time_taken_groupby["Expected Time to Complete (minutes)"].mean()
            
            # average_time_loan_type_list = []
            # for i in range(len(efficiency_df)):
            #     if average_time_loan_type["Expected Time to Complete (minutes)"][i] <= 100:
            #         average_time_loan_type_list.append(average_time_loan_type["Loan Type"][i])

            
            accuracy_df = suggestion_filter_df[suggestion_filter_df["Error Type"] != "No Error"]

            error_applications_count_list = []
            error_type_list = []
            error_type_unique_list = []
            for i in range(len(accuracy_df)):
                error_applications_count_list.append(accuracy_df.index[i])
                error_type_list.append(accuracy_df.iloc[i, accuracy_df.columns.get_loc("Error Type")])
                if accuracy_df.iloc[i, accuracy_df.columns.get_loc("Error Type")] not in error_type_unique_list:
                    error_type_unique_list.append(accuracy_df.iloc[i, accuracy_df.columns.get_loc("Error Type")])            
                # if suggestion_filter_df.iloc[i, suggestion_filter_df.columns.get_loc("Application Status")] == "Error":
                #     error_applications_count_list.append(suggestion_filter_df.index[i])
                #     if suggestion_filter_df.iloc[i, suggestion_filter_df.columns.get_loc("Error Type")] not in error_type_list:
                #         error_type_list.append(suggestion_filter_df.iloc[i, suggestion_filter_df.columns.get_loc("Error Type")])
            # error_type_count_set = set(error_type_list)
            # error_type_count_list = (list(error_type_count_set))
            calculate_most_frequent_error_type_list = Counter(error_type_list)
            most_frequent_error_type_list = calculate_most_frequent_error_type_list.most_common()

            most_frequent_error_type_selected_list = []
            if len(most_frequent_error_type_list) > 3:
                for i in range(3):
                    if most_frequent_error_type_list[i][0] not in most_frequent_error_type_selected_list:
                        most_frequent_error_type_selected_list.append(most_frequent_error_type_list[i][0])

            # def get_error_type_count(len):
            #     if len > 
            # st.write(most_frequent_error_type_list)
            # st.write(most_frequent_error_type_selected_list)
            # st.write(most_frequent_error_type_list[0][0])
            # print(most_frequent_error_type_list[0][0])
            # st.write(error_type_count_list)
            if len(error_applications_count_list) > 0:
                if len(most_frequent_error_type_list) > 3:
                    error_type_string = ", ".join(most_frequent_error_type_selected_list)
                else:
                    error_type_string = ", ".join(error_type_unique_list)

            effectivity_df = suggestion_filter_df[suggestion_filter_df["Ageing (days)"] < 2]

            effectivity_applications_count_list = []
            for i in range(len(effectivity_df)):
                effectivity_applications_count_list.append(effectivity_df.index[i]) 
            
            loan_processor_list = []
            for i in range(len(suggestion_filter_df)):
                if suggestion_filter_df.iloc[i, suggestion_filter_df.columns.get_loc("Loan Processor")] not in loan_processor_list:
                    loan_processor_list.append(suggestion_filter_df.iloc[i, suggestion_filter_df.columns.get_loc("Loan Processor")])
            loan_processor_string = ", ".join(loan_processor_list)

            suggestion_check = []

            c1, c2 = st.columns([3,1], gap = 'small')
            with c1:
                if len(productivity_applications_count_list) > 0 or len(efficiency_applications_count_list) > 0 or len(error_applications_count_list) > 0: 
                    st.markdown("<h style = 'font-size: 13px;'>Hi {},</h>".format(loan_processor_string), unsafe_allow_html = True)
                    if len(productivity_applications_count_list) > 0:
                        suggestion_check.append('productivity')
                        if len(productivity_applications_count_list) == 1:
                            st.markdown("<h style = 'font-size: 13px;'>**{}** application in your pipeline is anticipated to complete in **{}** minutes.</h>".format(len(productivity_applications_count_list), productivity_total_time_to_complete), unsafe_allow_html = True)
                        else:
                            st.markdown("<h style = 'font-size: 13px;'>**{}** applications in your pipeline are anticipated to complete in **{}** minutes.</h>".format(len(productivity_applications_count_list), productivity_total_time_to_complete), unsafe_allow_html = True)
                    
                    if len(efficiency_applications_count_list) > 0:
                        suggestion_check.append('efficiency')
                        if len(efficiency_applications_count_list) == 1:
                            st.markdown("<h style = 'font-size: 13px;'>**{}** application with an average closure time of **{}** minutes.</h>".format(len(efficiency_applications_count_list), efficiency_average_time_to_complete), unsafe_allow_html = True)
                        else:
                            st.markdown("<h style = 'font-size: 13px;'>**{}** applications (each) with an average closure time of **{}** minutes.</h>".format(len(efficiency_applications_count_list), efficiency_average_time_to_complete), unsafe_allow_html = True)

                    if len(error_applications_count_list) > 0:
                        suggestion_check.append('accuracy')
                        if len(most_frequent_error_type_list) == 1:
                            st.markdown("<h style = 'font-size: 13px;'>**{}** potential error linked to the existing pipeline: <br> **{}**</h>".format(len(most_frequent_error_type_list), error_type_string), unsafe_allow_html = True)
                        elif len(most_frequent_error_type_list) > 1 and len(most_frequent_error_type_list) <= 3:
                            st.markdown("<h style = 'font-size: 13px;'>**{}** potential errors linked to the existing pipeline: <br> **{}**</h>".format(len(most_frequent_error_type_list), error_type_string), unsafe_allow_html = True)
                        else:
                            st.markdown("<h style = 'font-size: 13px;'>Top **{}** potential errors linked to the existing pipeline: <br> **{}**</h>".format(len(most_frequent_error_type_selected_list), error_type_string), unsafe_allow_html = True)
                    
                    if len(effectivity_applications_count_list) > 0:
                        suggestion_check.append('effectivity')
                        if len(effectivity_applications_count_list) == 1:
                            st.markdown("<h style = 'font-size: 13px;'>**{}** application has high possibility of SLA breach.</h>".format(len(effectivity_applications_count_list)), unsafe_allow_html = True)
                        else:
                            st.markdown("<h style = 'font-size: 13px;'>**{}** applications have high possibility of SLA breach.</h>".format(len(effectivity_applications_count_list)), unsafe_allow_html = True)             
                else:
                    st.markdown("<h style = 'font-size: 13px;'>No suggestion</h>".format(loan_processor_string), unsafe_allow_html = True)
                
                # st.write("You have {} application/s with all the borrower documents ready in your pipeline.".format(len(productivity_applications_count_list)))
                # st.write("You have {} application/s in your pipeline with an average time of 30 minutes to complete.".format(len(efficiency_applications_count_list)))
                # st.write("You have {} application/s in your pipeline with issues {}.".format(len(error_applications_count_list), error_type_string))
                # st.write(productivity_applications_count_list)
                # st.dataframe(average_time_taken)
                # st.write(average_time_loan_type)
                # st.write(suggestion_filter_df)
                # st.write(suggestion_filter_df["Loan Number"])
                # st.write(productivity_applications_count_list)
                # st.write(productivity_df)
                # st.write(frequent_data_loan_progress)
                # st.write(frequent_data_loan_progress[frequent_data_loan_progress.index.isin(productivity_applications_count_list)])
                # st.write(loan_progress_df[loan_progress_df.index.isin(productivity_applications_count_list)])
                # st.write(loan_progress_df[loan_progress_df.index.isin(efficiency_applications_count_list)])
                # st.write(efficiency_df)
                # st.write(efficiency_average_time_to_complete)
                # st.write(average_time_loan_type_list)
                # st.write(efficiency_applications_count_list)
                # st.write(error_applications_count_list)
                # st.write(effectivity_applications_count_list)
                # st.write(average_time_to_complete)
                # st.write(total_time_to_complete)
                # st.write(accuracy_df)
                # st.write(suggestion_filter_df["Expected Time to Complete (minutes)"])
                # st.write(suggestion_filter_df["Expected Time to Complete (minutes)"].sum())
                # st.write()

            with c2:
                st.markdown("""<style>button{height: auto; padding-top: 5px !important; padding-bottom: 5px !important;}</style>""", unsafe_allow_html=True)
                
                if len(productivity_applications_count_list) > 0:
                    st.button(label = "Priortize", key = "productivity", help = "Click here to Priortize Applications")
                
                if len(efficiency_applications_count_list) > 0:
                    st.button(label = "Priortize", key = "efficiency", help = "Click here to Priortize Applications")
                
                if len(error_applications_count_list) > 0:
                    st.button(label = "Priortize", key = "accuracy", help = "Please be Watchful while Processing!", type = "primary")
                    st.markdown("""<style>.stbutton-key: accuracy {background-color: red;}</style>""", unsafe_allow_html=True)
                    # ("<style>.metric-label, .metric-value { font-size: 5px !important; }</style>", unsafe_allow_html = True)

                if len(effectivity_applications_count_list) > 0:
                    st.button(label = "Priortize", key = "effectivity", help = "Click here to Priortize Applications", type = "buttonBackground")
                    st.markdown("""<style>.button {background-color: rgb(204, 49, 49);}</style>""", unsafe_allow_html=True)
                    # st.markdown("""<style>div.stButton > button:first-child {background-color: rgb(204, 49, 49);}</style>""", unsafe_allow_html=True)
            # for i in range(suggestion_check):


            # st.markdown("<span style='color:lightgreen'>AI Suggestions</span>", unsafe_allow_html=True)
            
            # pending_loan_progress = frequent_data_loan_progress[frequent_data_loan_progress == 'Pending'].count().sum()
            # closed = frequent_data_loan_progress[frequent_data_loan_progress == 'Closed'].count().sum()

            # st.write("**Closed:** {}".format(closed), "&nbsp;&nbsp;&nbsp;&nbsp;**Pending:** {}".format(pending_loan_progress))
            
            # st.write('')
            # st.markdown("<h6 style = 'font-size: 18px;'>In Document Expiration Alerts by Loans Table</h6>", unsafe_allow_html = True)
            # expired_document_expiration_alerts = frequent_data_document_expiration_alerts[frequent_data_document_expiration_alerts == 'Expired'].count().sum()
            # expiring_soon_document_expiration_alerts = frequent_data_document_expiration_alerts[frequent_data_document_expiration_alerts == 'Expiring Soon'].count().sum()
            # not_expired_document_expiration_alerts = frequent_data_document_expiration_alerts[frequent_data_document_expiration_alerts == 'Not Expired'].count().sum()
            # pending_document_expiration_alerts = frequent_data_document_expiration_alerts[frequent_data_document_expiration_alerts == 'Pending'].count().sum()
            
            # st.write("**Expired:** {}".format(expired_document_expiration_alerts), "&nbsp;&nbsp;&nbsp;&nbsp;**Expiring Soon:** {}".format(expiring_soon_document_expiration_alerts), "&nbsp;&nbsp;&nbsp;&nbsp;**Not Expired:** {}".format(not_expired_document_expiration_alerts), "&nbsp;&nbsp;&nbsp;&nbsp;**Pending:** {}".format(pending_document_expiration_alerts))
    
    with st.container():
        st.markdown("<h3 style = 'text-align: center; font-size: 25px; padding-top: 45px;'>Loan Progress</h3>", unsafe_allow_html = True)

    # loan_progress_priortize = st.container()
    # with loan_progress_priortize:
        # @st.cache_data
        # def get_data_loan_progress():
        #     return loan_progress_df
        # st.write(productivity_applications_count_list)
        # default_status = []
        
        # if st.session_state in suggestion_check:
        #     st.write('yes')
        #     if all(st.session_state.values()) == False:
        #         default_status.append('False')
        #     if any(st.session_state.values()) == False:
        #         default_status.append('True')
        
        # st.write(st.session_state)
    
        # loan_progress_priortize = st.empty()
        # with st.empty():

        if st.session_state == '':
            st.session_state = 'False'
        
        # st.write(st.session_state)
        # st.write(all(st.session_state.values()))
        # st.write(any(st.session_state.values()))
        # st.write(st.session_state['efficiency'])
            # try:
                # if list(st.session_state.keys()) in suggestion_check:
        
        if any(st.session_state.values()) == False:
            filtered_data_df = loan_progress_df[loan_progress_df["Progress"].isin(loan_progress_df["Progress"].unique())]
            get_loan_progress_grid(filtered_data_df, 400)            
            
            # except:
            #     pass
        
            # st.write(st.session_state)
            # st.write(st.session_state('efficiency'))

        # loan_progress_priortize.write('Hi')

            # filtered_data_df = loan_progress_df[loan_progress_df["Progress"].isin(loan_progress_df["Progress"].unique())]
            # get_loan_progress_grid(filtered_data_df, 400)
        else:
            try:
                if st.session_state['productivity'] == True:
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
                if st.session_state['effectivity'] == True:
                    effectivity_priority_df = loan_progress_df[loan_progress_df.index.isin(effectivity_applications_count_list)]
                    get_loan_progress_grid(effectivity_priority_df, 250)
            except:
                pass

        # try:
        #     if not (st.session_state('productivity') and st.session_state('efficiency') and st.session_state('accuracy') and st.session_state('effectivity')):
        #         filtered_data_df = loan_progress_df[loan_progress_df["Progress"].isin(loan_progress_df["Progress"].unique())]
        #         get_loan_progress_grid(filtered_data_df, 400)
        # except:
        #     pass


        # st.session_state.clear()
        # print(st.session_state)

        # try:
        #     if productivity_priority_button:
        #         productivity_priority_df = loan_progress_df[loan_progress_df.index.isin(productivity_applications_count_list)]
        #         print('l2')
        #         get_loan_progress_grid(productivity_priority_df, 250)
        #         print('l4')
        # except:
        #     pass

        # try:
        #     if efficiency_priority_button:
        #         efficirncy_priority_df = loan_progress_df[loan_progress_df.index.isin(efficiency_applications_count_list)]
        #         get_loan_progress_grid(efficirncy_priority_df, 250)
        # except:
        #     pass
        
        # try:
        #         if accuracy_priority_button:
        #             accuracy_priority_df = loan_progress_df[loan_progress_df.index.isin(error_applications_count_list)]
        #             get_loan_progress_grid(accuracy_priority_df, 250)
        # except:
        #         pass    
        
        # try:
        #         if effectivity_priority_button:
        #             effectivity_priority_df = loan_progress_df[loan_progress_df.index.isin(effectivity_applications_count_list)]
        #             get_loan_progress_grid(effectivity_priority_df, 250)
        # except:
        #         pass

        # # if not (len(productivity_applications_count_list) > 0 and len(efficiency_applications_count_list) > 0 and len(error_applications_count_list) > 0 and len(effectivity_applications_count_list)) > 0:
        # try:
        #         if not (productivity_priority_button and efficiency_priority_button and accuracy_priority_button):
        #             filtered_data_df = loan_progress_df[loan_progress_df["Progress"].isin(loan_progress_df["Progress"].unique())]
        #             get_loan_progress_grid(filtered_data_df, 400)
        # except:
        #         pass


        # try:
        #     if productivity_priority_button:
        #         productivity_priority_df = loan_progress_df[loan_progress_df.index.isin(productivity_applications_count_list)]
        #         get_loan_progress_grid(productivity_priority_df, 250)
            
        #     elif efficiency_priority_button:
        #         efficiency_priority_df = loan_progress_df[loan_progress_df.index.isin(efficiency_applications_count_list)]
        #         get_loan_progress_grid(efficiency_priority_df, 250)

        #     elif accuracy_priority_button:
        #         accuracy_priority_df = loan_progress_df[loan_progress_df.index.isin(error_applications_count_list)]
        #         get_loan_progress_grid(accuracy_priority_df, 250)

        #     elif effectivity_priority_button:
        #         effectivity_priority_df = loan_progress_df[loan_progress_df.index.isin(effectivity_applications_count_list)]
        #         get_loan_progress_grid(effectivity_priority_df, 250)    
        # except:
        #     pass

        # try:
        #     if not (productivity_priority_button and efficiency_priority_button and accuracy_priority_button and effectivity_priority_button):
        #             filtered_data_df = loan_progress_df[loan_progress_df["Progress"].isin(loan_progress_df["Progress"].unique())]
        #             get_loan_progress_grid(filtered_data_df, 400)
        # except:
        #     pass
        # print(st.session_state)
        
        # try:    
        #     if productivity_priority_button:
        #         productivity_priority_df = loan_progress_df[loan_progress_df.index.isin(productivity_applications_count_list)]
        #         get_loan_progress_grid(productivity_priority_df, 250)
        # except:
        #     pass
                       
        # try:  
        #     if efficiency_priority_button:
        #         efficiency_priority_df = loan_progress_df[loan_progress_df.index.isin(efficiency_applications_count_list)]
        #         get_loan_progress_grid(efficiency_priority_df, 250)
        # except:
        #     pass    
        
        # try:
        #     if accuracy_priority_button:
        #         accuracy_priority_df = loan_progress_df[loan_progress_df.index.isin(error_applications_count_list)]
        #         get_loan_progress_grid(accuracy_priority_df, 250)
        # except:
        #     pass
            
        # try:
        #     if effectivity_priority_button:
        #         effectivity_priority_df = loan_progress_df[loan_progress_df.index.isin(effectivity_applications_count_list)]
        #         get_loan_progress_grid(effectivity_priority_df, 250)
        # except:
        #     pass
        
        # try:
        #     if not (productivity_priority_button and efficiency_priority_button and accuracy_priority_button and effectivity_priority_button):
        #         filtered_data_df = loan_progress_df[loan_progress_df["Progress"].isin(loan_progress_df["Progress"].unique())]
        #         get_loan_progress_grid(filtered_data_df, 400)
        # except:
        #     pass
        
        # filtered_data_df = loan_progress_df[loan_progress_df["Progress"].isin(loan_progress_df["Progress"].unique())]
        # get_loan_progress_grid(filtered_data_df, 400)

        # try:
        #     if not (productivity_priority_button and efficiency_priority_button and accuracy_priority_button):
        #         filtered_data_df = loan_progress_df[loan_progress_df["Progress"].isin(loan_progress_df["Progress"].unique())]
        #         get_loan_progress_grid(filtered_data_df, 400)
        # except:
        #     pass
            
        # progress_filter_component = JsCode("""
        #     # get filter instance
        #     const progress_filter_commponent = gridOptions.api.getFilterInstance('progress'); 

        #     # get filter model
        #     const model = progress_filter_component.getModel(); 

        #     # set filter model and update
        #     progress_filter_component.setModel({ values: loan_progress_df["Progress"].unique() });

        #     # refresh rows based on the filter (not automatic to allow for batching multiple filters)
        #     gridOptions.api.onFilterChanged();
        # """)

        # progress_filter_onFirstDataRendered = JsCode("""
        #     function progress_filter_onFirstDataRendered(parmas) {
        #     # console.log('The grid is now ready');
        #     var progressFilterComponent = parmas.api.getFilterInstance('Progress (%)');
        #     progressFilterComponent.setModel({type: 'inRange', filter: loan_progress_df["Progress"].unique(), filterTo: null,});
        #     parmas.api.onFilterChanged();
        #     }
        # """)

        # options = {
        # # "rowSelection": "multiple",
        # # "rowMultiSelectWithClick": True,
        # # "sideBar": ["columns", 'filters'],
        # # "enableRangeSelection": True,
        # "onFirstDataRendered": progress_filter_onFirstDataRendered
        # }    

# function onFirstDataRendered(parmas) {
#   # console.log('The grid is now ready');
#   var ageFilterComponent = parmas.api.getFilterInstance('age');
#   ageFilterComponent.setModel({
#     type: 'greaterThan',
#     filter: 18,
#     filterTo: null,
#   });

#   # get filter instance
#             const progress_filter_commponent = gridOptions.api.getFilterInstance('progress'); 

#             # get filter model
#             const model = progress_filter_component.getModel(); 

#             # set filter model and update
#             progress_filter_component.setModel({ values: loan_progress_df["Progress"].unique() });

#             # refresh rows based on the filter (not automatic to allow for batching multiple filters)
#             gridOptions.api.onFilterChanged();

#   parmas.api.onFilterChanged();
# }
        
            # st.markdown("<h3 style = 'text-align: center; font-size: 25px; padding-top: 45px;'>Loan Progress</h3>", unsafe_allow_html = True)
            # gb_loan_progress.configure_default_column(min_column_width = 110, resizable = True, filterable = True, sortable = True, groupable = True)
            # gb_loan_progress.configure_column(field = "Loan Type", header_name = "Loan Type", wrapHeaderText = True, autoHeaderHeight = True)
            # gb_loan_progress.configure_column(field = "Loan Number", header_name = "Loan Number", wrapHeaderText = True, autoHeaderHeight = True, sort = 'asc')
            # gb_loan_progress.configure_column(field = "Progress", header_name = "Progress (%)", cellStyle = cellstyle_jscode_loan_progress, wrapHeaderText = True, autoHeaderHeight = True)
            # gb_loan_progress.configure_column(field = "ExpRate Lock", header_name = "Rate Lock (10%)", cellStyle = cellstyle_jscode_loan_progress, wrapHeaderText = True, autoHeaderHeight = True)
            # gb_loan_progress.configure_column(field = "ExpAppraisal", header_name = "Appraisal (20%)", cellStyle = cellstyle_jscode_loan_progress, wrapHeaderText = True, autoHeaderHeight = True)
            # gb_loan_progress.configure_column(field = "Exp_Title", header_name = "Title (20%)", cellStyle = cellstyle_jscode_loan_progress, wrapHeaderText = True, autoHeaderHeight = True)
            # gb_loan_progress.configure_column(field = "ExpCredit_Exp", header_name = "Credit Exp (15%)", cellStyle = cellstyle_jscode_loan_progress, wrapHeaderText = True, autoHeaderHeight = True)
            # gb_loan_progress.configure_column(field = "Exp_VVOE", header_name = "VVOE (5%)", cellStyle = cellstyle_jscode_loan_progress, wrapHeaderText = True, autoHeaderHeight = True)
            # gb_loan_progress.configure_column(field = "Exp_HOI", header_name = "HOI (5%)", cellStyle = cellstyle_jscode_loan_progress, wrapHeaderText = True, autoHeaderHeight = True)
            # gb_loan_progress.configure_column(field = "Exp_Payoff", header_name = "Payoffs (10%)", cellStyle = cellstyle_jscode_loan_progress, wrapHeaderText = True, autoHeaderHeight = True)
            # gb_loan_progress.configure_column(field = "Exp_Income", header_name = "Income Exp (15%)", cellStyle = cellstyle_jscode_loan_progress, wrapHeaderText = True, autoHeaderHeight = True)
            # gb_loan_progress.configure_column(field = "Ageing (days)", header_name = "Ageing (days)", wrapHeaderText = True, autoHeaderHeight = True)
            # gb_loan_progress.configure_column(field = "Borrower Intent to Continue Date", header_name = "Borrower Intent to Continue Date", wrapHeaderText = True, autoHeaderHeight = True)
            # grid_options_loan_progress = gb_loan_progress.build()
            # loan_progress_table = AgGrid(frequent_data_loan_progress, gridOptions = grid_options_loan_progress, columns_auto_size_mode = ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW, fit_columns_on_grid_load = True, height = 400, reload_data = True, allow_unsafe_jscode = True)
            # st.markdown("<h6 style = font-size: 5px;'>Closed -- Loan process is completed &emsp; Pending -- Awaits document to be submitted</h6>", unsafe_allow_html = True)

    # with st.empty():
        st.markdown("<h6 style = font-size: 5px;'>Closed -- Loan process is completed &emsp; Pending -- Awaits document to be submitted</h6>", unsafe_allow_html = True)

    with st.container():
        # @st.cache_data
        # def get_data_document_expiration_alerts():
        #     return document_expiration_alerts_df
    
           
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

        st.markdown("<h3 style='text-align: center; font-size: 25px; padding-top: 45px;'>Document Expiration Alerts by Loans</h3>", unsafe_allow_html = True)
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
    answers = ["Overall Productivity for Apr'23 - 90%,  May'23 - 92%,  Jun'23 - 90%", 
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
