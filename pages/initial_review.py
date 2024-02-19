import streamlit as st
import pandas as pd
import openpyxl as xl
from app import program, program_type, review_type, review_date


# Load data to be reviewed based on params from page 1
@st.cache_data
def load_standards():
    if st.session_state.ptype == "CLA":
        standards = pd.read_excel(fr"files\compliance_standards.xlsx", sheet_name="CLA Standards")
    elif st.session_state.ptype == "NGH":
        standards = pd.read_excel(fr"files\compliance_standards.xlsx", sheet_name="NGH Standards")

    tobola_standards = pd.read_excel(fr"files\compliance_standards.xlsx", sheet_name="TOBOLA Standards")

    review_standards = pd.merge(standards, tobola_standards,
                                 on=["SECTION", "STANDARD", "DESCRIPTION"],
                                 how='outer')

    review_standards["COMPLIANCE"] = True
    review_standards['FINDING'] = ''

    return review_standards


@st.cache_data
def load_params():
    if 'program' not in st.session_state:
        st.session_state.program = program
    if 'ptype' not in st.session_state:
        st.session_state.ptype = program_type
    if 'rtype' not in st.session_state:
        st.session_state.rtype = review_type
    if 'review_date' not in st.session_state:
        st.session_state.review_date = review_date
    if 'current_standard' not in st.session_state:
        st.session_state.current_standard = 0

def write_report():
    workbook = xl.Workbook("files/templates/initial_review.xlsx")
    sheet = workbook.active
    sheet["B1"] = program
    sheet["B2"] = manager
    sheet["B3"] = compliance_progress
    sheet["B4"] = review_date

    writer = pd.ExcelWriter(fr"files/templates/initial_review.xlsx", engine='openpyxl')

    results.to_excel(writer, startrow=7, index=False, Header=False)


standards = load_standards()
load_params()


if 'results' not in st.session_state:
    st.session_state.results = pd.DataFrame(columns=['SECTION', 'STANDARD', 'DESCRIPTION', 'COMPLIANCE', 'FINDING'])


tab1, tab2 = st.tabs(["Review", "Results"])

with tab1:

    @st.cache_data
    def audit_loader():
        current_index = st.session_state.current_standard

        # Check if data for the current index already exists
        existing_row = st.session_state.results[st.session_state.results.index == current_index]

        if not existing_row.empty:
            # Update existing row
            st.session_state.results.loc[current_index, 'SECTION'] = st.session_state.SECTION
            st.session_state.results.loc[current_index, 'STANDARD'] = st.session_state.STANDARD
            st.session_state.results.loc[current_index, 'DESCRIPTION'] = st.session_state.DESCRIPTION
            st.session_state.results.loc[current_index, 'COMPLIANCE'] = st.session_state.COMPLIANCE
            st.session_state.results.loc[current_index, 'FINDING'] = st.session_state.FINDING
        else:
            # Append a new row
            new_row = pd.DataFrame({
                "SECTION": [st.session_state.SECTION],
                "STANDARD": [st.session_state.STANDARD],
                "DESCRIPTION": [st.session_state.DESCRIPTION],
                "COMPLIANCE": [st.session_state.COMPLIANCE],
                "FINDING": [st.session_state.FINDING]
            }, index=[current_index])

            st.session_state.results = pd.concat([st.session_state.results, new_row]).drop_duplicates()


    header_box = st.container()
    with header_box:
        l, r = st.columns([4,1])

        with l:
            st.subheader(fr"{st.session_state.program} {st.session_state.rtype} Review - "
                         fr"{st.session_state.review_date.month}/{st.session_state.review_date.day}/{st.session_state.review_date.year}")

        with r:
            build_initial_report_button = st.button('Build Report', disabled=True)


    current = st.session_state.current_standard
    audit_box = st.container()

    with audit_box:

        try:
            # SECTION
            if 'SECTION' not in st.session_state:
                st.session_state.SECTION = format(standards['SECTION'][standards.index == 0].unique()[0])
                section = st.header(standards['SECTION'][standards.index == 0].unique()[0], divider='blue')
            else:
                st.session_state.SECTION = format(standards['SECTION'][standards.index == current].unique()[0])
                section = st.header(standards['SECTION'][standards.index == current].unique()[0], divider='blue')

            # STANDARD
            standard = st.write(standards['STANDARD'][standards.index == current].unique()[0])
            if 'STANDARD' not in st.session_state:
                st.session_state.STANDARD = format(standards['STANDARD'][standards.index == 0].unique()[0])
            else:
                st.session_state.STANDARD = format(standards['STANDARD'][standards.index == current].unique()[0])

            l, c, r = st.columns([3,1,3])

            # DESCRIPTION
            with l:
                st.write("DESCRIPTION")
                description = st.write(standards['DESCRIPTION'][standards.index == current].unique()[0])
                if 'DESCRIPTION' not in st.session_state:
                    st.session_state.DESCRIPTION = format(standards['DESCRIPTION'][standards.index == 0].unique()[0])
                else:
                    st.session_state.DESCRIPTION = standards['DESCRIPTION'][standards.index == current].unique()[0]

            # COMPLIANCE
            with c:
                if 'COMPLIANCE' not in st.session_state:
                    compliance = st.radio("COMPLIANCE", options=[True, False], key='COMPLIANCE')
                else:
                    compliance = st.radio("COMPLIANCE", options=[True, False], key='COMPLIANCE')

            # FINDING
            def finding_check():
                try:
                    data = st.session_state.results.FINDING[st.session_state.results.index == current].unique()[0]
                except IndexError:
                    data = ''

                return data


            with r:
                if 'FINDING' not in st.session_state:
                    finding = st.text_area(label='FINDING',
                                           key='FINDING')
                else:
                    finding = st.text_area(label='FINDING',
                                           value= finding_check(),
                                           key='FINDING')

        except IndexError:
            pass

        results = st.session_state.results


    with st.sidebar:
        all_count = results['COMPLIANCE'].count()
        true_count = results['COMPLIANCE'][results['COMPLIANCE']].count()
        compliance_progress = true_count/all_count
        try:
            st.header(fr"{round(compliance_progress*100)}% Compliance")
            st.progress(compliance_progress)
        except ValueError:
            st.header("Start Review")

        st.write('Standards Reviewed = ', format(all_count))
        st.write('TOTAL Standard  = ', format(standards['COMPLIANCE'].count()-1))

        for section in standards["SECTION"].unique():
            with st.expander(section):
                for i, row in standards.iterrows():
                    if row.SECTION == section:
                        standard_button = st.button(fr"{i} | {row.STANDARD}")
                    if standard_button:
                        st.session_state.current_standard = i


    navigation_box = st.container()

    with navigation_box:
        l, r = st.columns(2)

        with l:
            prev_button = st.button("previous",
                                    use_container_width=True,
                                    on_click=audit_loader)
        with r:
            next_button = st.button("next",
                                    use_container_width=True,
                                    on_click=audit_loader)

        if prev_button:
            if st.session_state.current_standard == 0:
                pass
            else:
                st.session_state.current_standard = st.session_state.current_standard-1

        elif next_button:
            st.session_state.current_standard = st.session_state.current_standard+1


    if all_count >= standards['SECTION'].count() - 1:
        l, r = st.columns([1, 3])
        with l:
            st.header("All Standards Reviewed")
        with r:
            st.download_button(
                label="DownloadReport",
                data=write_report(),
                file_name="report_test.xlsx",
                mime="application/vnd.ms-excel")


with tab2:
    st.dataframe(results, use_container_width=True)

# TODO
# create progress bar under the navigation box
