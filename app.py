import pandas as pd
import streamlit as st
from st_pages import Page, show_pages, hide_pages

st.set_page_config(page_title="TOBOLA QA Review", layout="wide")


@st.cache_data
def building_params():
    params = pd.DataFrame()
    params["ptype"] = st.session_state.ptype
    params["program"] = st.session_state.program
    params["review_date"] = st.session_state.review_date
    params["review_type"] = st.session_state.rtype
    manager = pd.read_excel(fr"files/compliance_standards.xlsx", sheet_name="Programs")
    st.session_state.manager = manager["Manager"][manager["Name"] == st.session_state.program].unique()[0]
    params["manager"] = st.session_state.manager
    print(params)



# Pages for the entire application
show_pages(
    [
        Page("app.py", "Report Parameters"),
        Page(fr"pages/initial_review.py", "Initial Review"),
        Page(fr"pages/final_review.py", "Final Review"),
    ]
)


# Program type selection
program_type = st.radio("Program Type", options=["CLA", "NGH"], key="ptype")

# Program options
programs = pd.read_excel(fr"files\compliance_standards.xlsx", sheet_name="Programs")


# Filter for program selection
def ptype_filter():
    return programs.Name[programs.Type == st.session_state['ptype']]


# Program being reviewed
program = st.radio('Program', options=f.ptype_filter(), key="program")

# Date of QA review
review_date = st.date_input('Review Date', key='review_date')

# Review type selection
review_type = st.radio("Review Type", options=["Initial", "Final"], key='rtype')


# Button to initiate the review
start_review = st.button("Begin Review")

if start_review:
    building_params()
    if st.session_state['rtype'] == "Initial":
        st.session_state['current_standard'] = 0
        st.switch_page(fr"pages/initial_review.py")
    elif st.session_state['rtype'] == "Final":
        st.switch_page(fr"pages/final_review.py")



