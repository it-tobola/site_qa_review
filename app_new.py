import pandas as pd
import openpyxl as xl
import streamlit as st
import backend

st.set_page_config(page_title="TOBOLA QA Review", layout="wide")

@st.cache_data
def load_standards():
    # Load data from Excel file
    if st.session_state.ptype == "CLA":
        standards = pd.read_excel(fr"files\compliance_standards.xlsx", sheet_name="CLA Standards")
    elif st.session_state.ptype == "NGH":
        standards = pd.read_excel(fr"files\compliance_standards.xlsx", sheet_name="NGH Standards")

    tobola_standards = pd.read_excel(fr"files\compliance_standards.xlsx", sheet_name="TOBOLA Standards")

    # Merge and clean the data
    review_standards = pd.DataFrame(columns=["SECTION", "STANDARD", "DESCRIPTION", "COMPLIANCE", "FINDING", "Default"])
    review_standards = pd.merge(review_standards, tobola_standards,
                                 on=["SECTION", "STANDARD", "DESCRIPTION", "Default"],
                                 how='outer').drop_duplicates()

    review_standards = pd.merge(standards, review_standards,
                                 on=["SECTION", "STANDARD", "DESCRIPTION", "Default"],
                                 how='outer').drop_duplicates()

    review_standards["COMPLIANCE"] = review_standards.Default
    review_standards = review_standards[["SECTION", "STANDARD", "DESCRIPTION", "COMPLIANCE", "FINDING"]]

    return review_standards


def finding_check():
    try:
        data = results.FINDING[results.index == current_standard].unique()[0]
    except IndexError:
        data = ''

    return data


def append_finding():

    # Modify the DataFrame as needed
    current_standard = st.session_state.current_standard
    st.session_state.results.loc[current_standard, 'SECTION'] = review_standards['SECTION'][current_standard]
    st.session_state.results.loc[current_standard, 'STANDARD'] = review_standards['STANDARD'][current_standard]
    st.session_state.results.loc[current_standard, 'DESCRIPTION'] = review_standards['DESCRIPTION'][current_standard]
    st.session_state.results.loc[current_standard, 'COMPLIANCE'] = st.session_state.compliance
    st.session_state.results.loc[current_standard, 'FINDING'] = st.session_state.finding

    return st.session_state.results


def begin_review():
    st.session_state.run = True
    return st.session_state.run


tab1, tab2 = st.tabs(["Review", "Results"])

if "current_standard" not in st.session_state:
    st.session_state.current_standard = 0
current_standard = st.session_state.current_standard

if "run" not in st.session_state:
    st.session_state.run = False

with tab1:
    with st.expander("Parameters"):
        l, c, r = st.columns(3)
        with l:
            program_options = pd.read_excel(fr"files\compliance_standards.xlsx", sheet_name="Programs")
            program = st.selectbox('Program', options=program_options["Name"], key="program")
        with c:
            review_date = st.date_input('Review Date', key='review_date')
        with r:
            review_type = st.selectbox("Review Type", options=["Initial", "Final"], key='rtype')

        start_review = st.button("Begin Review", use_container_width=True, on_click=begin_review)

    if st.session_state.run:
        st.divider()
        program_name = program_options.loc[program_options["Name"] == program, "Type"].iloc[0]
        st.session_state.ptype = program_name

        review_standards = load_standards()
        if "results" not in st.session_state:
            st.session_state.results = pd.DataFrame(columns=['SECTION', 'STANDARD', 'DESCRIPTION', 'COMPLIANCE', 'FINDING'])

        results = st.session_state.results

        header_box = st.container()
        with header_box:
            st.subheader(fr"{program} {review_type} Review - "
                         fr"{review_date.month}/{review_date.day}/{review_date.year}")
        audit_box = st.container()

        if current_standard >= len(review_standards):
            st.warning("All standards have been reviewed.")
        try:
            section = st.header(review_standards['SECTION'].iloc[current_standard], divider='blue')

            standard = st.write(review_standards['STANDARD'][current_standard])

            l, c, r = st.columns([3, 1, 3])
            with l:
                st.write("DESCRIPTION")
                description = st.write(review_standards['DESCRIPTION'][current_standard])

            with c:
                compliance = st.radio("COMPLIANCE", options=[True, False], key='compliance')

            with r:
                finding = st.text_area(label='FINDING', value=finding_check(), key='finding')
        except IndexError:
            pass

        navigation_box = st.container()

        with navigation_box:
            def prev_button_click():
                if st.session_state.current_standard == 0:
                    pass
                else:
                    st.session_state.current_standard = st.session_state.current_standard-1
                return st.session_state.current_standard


            def next_button_click():
                append_finding()
                st.session_state.current_standard += 1
                return st.session_state.current_standard


            l, r = st.columns(2)
            with l:
                prev_button = st.button("previous", use_container_width=True, on_click=prev_button_click)
            with r:
                next_button = st.button("next", use_container_width=True, on_click=next_button_click)

with st.sidebar:
    if results is not None:
        all_count = review_standards['STANDARD'].count()
        st.sidebar.subheader("Compliance Summary")
        compliance_counts = results['COMPLIANCE'].value_counts()
        st.sidebar.write(f"Compliant: {compliance_counts.get(True, 0)}")
        st.sidebar.write(f"Non-compliant: {compliance_counts.get(False, 0)}")
        true_count = compliance_counts.get(True, 0)
        false_count = compliance_counts.get(False, 0)
        compliance_score = round(((all_count-false_count)/all_count)*100)
        reviewed_count = true_count + false_count
        st.sidebar.write(f"Pending Review: {all_count - reviewed_count}")
        st.sidebar.divider()
        st.sidebar.write(f"Current Compliance: {compliance_score}%")
        st.sidebar.progress(compliance_score)
    else:
        st.sidebar.warning("Results dataframe is not initialized. Please load the standards first.")

navigation_box.progress(reviewed_count/all_count)

with tab2:
    results_box = st.container()
    with results_box:
        st.write(fr"{program} Compliance Score: {compliance_score}%")
        st.divider()
    if st.session_state.run:
        st.dataframe(results, use_container_width=True)
        st.divider()
    else:
        st.warning("Results dataframe is not initialized. Please load the standards first.")
