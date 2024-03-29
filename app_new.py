import pandas as pd
import openpyxl as xl
import streamlit as st
import backend

st.set_page_config(page_title="TOBOLA QA Review", layout="wide")
@st.cache_data
def load_standards():
    # Load data from Excel file
    if st.session_state.ptype == "CLA":
        standards = pd.read_excel(fr"files/compliance_standards.xlsx", sheet_name="CLA Standards")
    elif st.session_state.ptype == "NGH":
        standards = pd.read_excel(fr"files/compliance_standards.xlsx", sheet_name="NGH Standards")

    tobola_standards = pd.read_excel(fr"files/compliance_standards.xlsx", sheet_name="TOBOLA Standards")

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


def load_final_standards(file):
    standards = pd.read_excel(file, sheet_name="Audit")
    standards.columns = ['Section',
                           'Standard',
                           'Description',
                           'Initial Compliance',
                           'Finding',
                           'Manager Response']

    standards = standards[['Section',
                               'Standard',
                               'Description',
                               'Initial Compliance',
                               'Finding',
                               'Manager Response']]

    standards["Response Verification"] = ""
    standards["Final Notes"] = ""
    standards["Final Compliance"] = ""


    report = standards[standards["Initial Compliance"] == False]
    standards_to_review = report.reset_index(drop=True)
    standards = standards[standards["Initial Compliance"] == True]
    return standards_to_review, standards


def finding_check():
    try:
        data = results.FINDING[results.index == current_standard].unique()[0]
    except IndexError:
        data = ''

    return data


def append_finding():
    current_standard = st.session_state.current_standard

    if review_type == "Initial":
        # Modify the DataFrame as needed
        st.session_state.results.loc[current_standard, 'SECTION'] = review_standards['SECTION'][current_standard]
        st.session_state.results.loc[current_standard, 'STANDARD'] = review_standards['STANDARD'][current_standard]
        st.session_state.results.loc[current_standard, 'DESCRIPTION'] = review_standards['DESCRIPTION'][current_standard]
        st.session_state.results.loc[current_standard, 'COMPLIANCE'] = st.session_state.compliance
        st.session_state.results.loc[current_standard, 'FINDING'] = st.session_state.finding
    elif review_type == "Final":
        # Modify the DataFrame based on user input during the final review
        st.session_state.results.loc[current_standard, 'Section'] = review_standards['Section'][current_standard]
        st.session_state.results.loc[current_standard, 'Standard'] = review_standards['Standard'][current_standard]
        st.session_state.results.loc[current_standard, 'Description'] = review_standards['Description'][current_standard]
        st.session_state.results.loc[current_standard, 'Initial Compliance'] = review_standards['Initial Compliance'][current_standard]
        st.session_state.results.loc[current_standard, 'Finding'] = review_standards['Finding'][current_standard]
        st.session_state.results.loc[current_standard, 'Manager Response'] = review_standards['Manager Response'][current_standard]
        st.session_state.results.loc[current_standard, 'Response Verification'] = st.session_state.response_verification  # Update with user input
        st.session_state.results.loc[current_standard, 'Final Notes'] = st.session_state.final_notes  # Update with user input
        # Update 'Final Compliance' based on 'Response Verification'
        st.session_state.results.loc[current_standard, 'Final Compliance'] = st.session_state.response_verification

    return st.session_state.results



    return st.session_state.results


def begin_review():
    st.session_state.run = True
    program_type = program_options.loc[program_options["Name"] == program, "Type"].iloc[0]
    st.session_state.ptype = program_type
    return st.session_state.run


def prev_button_click():
    if st.session_state.current_standard == 0:
        pass
    else:
        st.session_state.current_standard = st.session_state.current_standard - 1
    return st.session_state.current_standard


def next_button_click():
    append_finding()
    st.session_state.current_standard += 1
    return st.session_state.current_standard

def fr_next_button_click():
    append_finding()
    st.session_state.current_standard += 1
    return st.session_state.current_standard


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
            program_options = pd.read_excel(fr"files/compliance_standards.xlsx", sheet_name="Programs")
            program = st.selectbox('Program', options=program_options["Name"], key="program")
        with c:
            review_date = st.date_input('Review Date', key='review_date')
        with r:
            review_type = st.selectbox("Review Type", options=["Initial", "Final"], key='rtype')

        if review_type == "Final":
            initial_report = st.file_uploader("Initial Report")
        start_review = st.button("Begin Review", use_container_width=True, on_click=begin_review)

    if st.session_state.run:
        st.divider()
        if st.session_state.rtype == "Initial":
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

                l, r = st.columns(2)
                with l:
                    prev_button = st.button("previous", use_container_width=True, on_click=prev_button_click)
                with r:
                    next_button = st.button("next", use_container_width=True, on_click=next_button_click)

        elif st.session_state.rtype == "Final":
            review_standards, results = load_final_standards(initial_report)
            review_date = pd.read_excel(initial_report, sheet_name="Report")
            review_date = review_date.iloc[2,1]

            results.columns = ['Section',
                               'Standard',
                               'Description',
                               'Initial Compliance',
                               'Finding',
                               'Manager Response',
                               'Response Verification',
                               'Final Notes',
                               'Final Compliance']

            if "results" not in st.session_state:
                st.session_state.results = pd.DataFrame(columns=['Section',
                               'Standard',
                               'Description',
                               'Initial Compliance',
                               'Finding',
                               'Manager Response',
                               'Response Verification',
                               'Final Notes',
                               'Final Compliance'])

            header_box = st.container()
            with header_box:
                st.subheader(fr"{program} {review_type} Review - "
                             fr"{review_date.month}/{review_date.day}/{review_date.year}")

            audit_box = st.container()
            if current_standard >= len(review_standards):
                st.warning("All standards have been reviewed.")
            try:
                section = st.header(review_standards['Section'].iloc[current_standard], divider='blue')

                standard = st.write(review_standards['Standard'][current_standard])

                l, r = st.columns([2, 1])
                st.divider()
                with l:
                    st.write("Description")
                    description = st.write(review_standards['Description'][current_standard])

                    with st.expander("Finding", expanded=True):
                        finding = st.write(fr"{review_standards.Finding[review_standards.index == current_standard].unique()[0]}")
                    with st.expander("Manager Response", expanded=True):
                        mgr_response = st.write(fr"{review_standards['Manager Response'][review_standards.index == current_standard].unique()[0]}")

                with r:
                    response_verification = st.radio(label="This standard is now satisfied.",
                                                     options=["False", "True"],
                                                     key="response_verification")
                    final_notes = st.text_area("Final Notes", key='final_notes')
                    navigation_box = st.container()

                    with navigation_box:
                        l, r = st.columns(2)
                        with l:
                            prev_button = st.button("previous", use_container_width=True, on_click=prev_button_click)
                        with r:
                            next_button = st.button("next", use_container_width=True, on_click=fr_next_button_click)


            except IndexError:
                pass

with st.sidebar:
    if review_type == "Initial":
        if "results" in st.session_state:
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
    elif review_type == "Final":
        if "results" in st.session_state:
            all_count = review_standards['Standard'].count()
            st.sidebar.subheader("Compliance Summary")
            st.sidebar.write(f"Previously Non-compliant: {all_count}")
            compliance_counts = results['Initial Compliance'].value_counts()
            initial_true_count = compliance_counts.get(True, 0)
            initial_false_count = compliance_counts.get(False, 0)
            total_count = initial_true_count + initial_false_count
            pending_count = all_count - st.session_state.results['Standard'].count()
            final_compliance_counts = st.session_state.results["Final Compliance"].value_counts()
            final_true_count = final_compliance_counts["True"]
            final_false_count = final_compliance_counts["False"]
            reviewed_count = final_true_count + final_false_count

            compliance_score = round(((total_count-(final_false_count))/total_count)*100)
            st.sidebar.write(f"Initial Compliance: {compliance_score}%")
            st.sidebar.progress(compliance_score)
            st.sidebar.divider()


            st.write(fr'Pending Review: {pending_count}')
            st.write(fr"Compliant: {final_true_count}")
            st.write(fr"Non-Compliant: {final_false_count}")
    else:
        st.sidebar.warning("Results dataframe is not initialized. Please load the standards first.")


with tab2:
    results_box = st.container()
    if "results" in st.session_state:
        with results_box:
            st.write(fr"{program} Compliance Score: {compliance_score}%")
            st.divider()
    if st.session_state.run:
        st.dataframe(st.session_state.results, use_container_width=True)
        st.divider()
    else:
        st.warning("Results dataframe is not initialized. Please load the standards first.")

    if reviewed_count >= all_count:
        review_complete = st.checkbox("Completed Review")

        if review_complete:
            if review_type == "Initial":
                merged_results = pd.merge(results, st.session_state.results, on="STANDARD")
            elif review_type == "Final":
                # Merge the data
                merged_results = pd.concat([results, st.session_state.results])

            merged_results.drop_duplicates()
            download = st.download_button('Download Report',
                                          data=merged_results.reset_index(drop=True).to_csv(index=False),
                                          file_name=fr"{program}_{review_date.month}/{review_date.year}.csv",
                                          use_container_width=True)
