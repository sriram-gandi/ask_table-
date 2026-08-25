import os
import sys
import tempfile

import streamlit as st


# ==============================================
# PROJECT PATH
# ==============================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

if PROJECT_ROOT not in sys.path:

    sys.path.insert(
        0,
        PROJECT_ROOT
    )


# ==============================================
# IMPORTS
# ==============================================

from app.core.dependencies import (
    create_db_manager,
    create_ingestion_service,
    create_analysis_service
)

from app.services.chart_service import (
    ChartService
)


# ==============================================
# PAGE CONFIG
# ==============================================

st.set_page_config(
    page_title="AskTable AI",
    page_icon="📊",
    layout="wide"
)


# ==============================================
# SESSION STATE INITIALIZATION
# ==============================================

if "db_manager" not in st.session_state:

    st.session_state.db_manager = (
        create_db_manager()
    )


if "ingestion_service" not in st.session_state:

    st.session_state.ingestion_service = (
        create_ingestion_service(
            st.session_state.db_manager
        )
    )


if "analysis_service" not in st.session_state:

    st.session_state.analysis_service = (
        create_analysis_service(
            st.session_state.db_manager
        )
    )


if "ingestion_results" not in st.session_state:

    st.session_state.ingestion_results = []


if "analysis_result" not in st.session_state:

    st.session_state.analysis_result = None


# ==============================================
# HELPER FUNCTION
# ==============================================

def save_uploaded_files(
    uploaded_files
):

    file_paths = []

    temp_dir = tempfile.mkdtemp()

    for uploaded_file in uploaded_files:

        file_path = os.path.join(
            temp_dir,
            uploaded_file.name
        )

        with open(
            file_path,
            "wb"
        ) as file:

            file.write(
                uploaded_file.getbuffer()
            )

        file_paths.append(
            file_path
        )

    return file_paths


# ==============================================
# HEADER
# ==============================================

st.title(
    "📊 AskTable AI"
)

st.caption(
    "Upload multiple datasets and ask questions "
    "across your data."
)


# ==============================================
# SIDEBAR
# ==============================================

with st.sidebar:

    st.header(
        "📁 Upload Data"
    )

    uploaded_files = st.file_uploader(

        "Upload CSV or Excel files",

        type=[
            "csv",
            "xlsx",
            "xls"
        ],

        accept_multiple_files=True
    )


    if uploaded_files:

        if st.button(
            "Process Files",
            type="primary",
            use_container_width=True
        ):

            try:

                with st.spinner(
                    "Ingesting files..."
                ):

                    file_paths = (
                        save_uploaded_files(
                            uploaded_files
                        )
                    )

                    results = (
                        st.session_state
                        .ingestion_service
                        .ingest_files(
                            file_paths
                        )
                    )

                    st.session_state.ingestion_results = (
                        results
                    )

                    st.session_state.analysis_result = (
                        None
                    )

                st.success(
                    f"{len(results)} file(s) processed."
                )

            except Exception as error:

                st.error(
                    f"Ingestion failed: {error}"
                )


    # ==========================================
    # DATASET SELECTION
    # ==========================================

    if st.session_state.ingestion_results:

        st.divider()

        st.subheader(
            "Datasets"
        )

        file_map = {

            result["file_name"]:
            result["file_id"]

            for result in
            st.session_state.ingestion_results
        }


        selected_file_names = st.multiselect(

            "Select datasets",

            options=list(
                file_map.keys()
            ),

            default=list(
                file_map.keys()
            )
        )


        selected_file_ids = [

            file_map[file_name]

            for file_name
            in selected_file_names
        ]

    else:

        selected_file_ids = []


# ==============================================
# DATASET OVERVIEW
# ==============================================

if st.session_state.ingestion_results:

    st.subheader(
        "Uploaded Datasets"
    )

    columns = st.columns(
        min(
            len(
                st.session_state
                .ingestion_results
            ),
            3
        )
    )


    for index, result in enumerate(
        st.session_state.ingestion_results
    ):

        with columns[
            index % len(columns)
        ]:

            st.info(
                f"📄 **{result['file_name']}**"
            )

            st.caption(
                f"ID: {result['file_id']}"
            )


# ==============================================
# QUESTION INPUT
# ==============================================

st.divider()

st.subheader(
    "Ask Your Data"
)


question = st.text_area(

    "What would you like to know?",

    placeholder=(
        "Example: Compare sales across regions"
    ),

    height=100
)


analyze_button = st.button(

    "🔍 Analyze",

    type="primary",

    disabled=(
        not selected_file_ids
        or not question.strip()
    )
)


# ==============================================
# ANALYSIS
# ==============================================

if analyze_button:

    try:

        with st.spinner(
            "Analyzing data..."
        ):

            result = (
                st.session_state
                .analysis_service
                .analyze(

                    question=question,

                    selected_file_ids=
                    selected_file_ids
                )
            )

            st.session_state.analysis_result = (
                result
            )

    except Exception as error:

        st.error(
            f"Analysis failed: {error}"
        )


# ==============================================
# RESULTS
# ==============================================

result = (
    st.session_state.analysis_result
)


if result:

    st.divider()


    # ==========================================
    # ERROR
    # ==========================================

    if result.get("error"):

        st.error(
            result["error"]
        )


    else:

        # ======================================
        # ANSWER
        # ======================================

        final_answer = result.get(
            "final_answer"
        )

        if final_answer:

            answer = final_answer.get(
                "answer"
            )

            if answer:

                st.subheader(
                    "Answer"
                )

                st.success(
                    answer
                )


        # ======================================
        # CHART
        # ======================================

        query_result = result.get(
            "query_result"
        )

        visualization_required = result.get(
            "visualization_required",
            False
        )

        visualization_plan = result.get(
            "visualization_plan"
        )


        if (
            visualization_required
            and visualization_plan
            and query_result is not None
            and not query_result.empty
        ):

            st.subheader(
                "Visualization"
            )

            try:

                chart = (
                    ChartService
                    .create_chart(

                        dataframe=
                        query_result,

                        visualization_plan=
                        visualization_plan
                    )
                )

                if chart is not None:

                    st.plotly_chart(
                        chart,
                        use_container_width=True
                    )

            except Exception as error:

                st.warning(
                    "Chart generation failed."
                )

                st.caption(
                    str(error)
                )


        # ======================================
        # DATA TABLE
        # ======================================

        if (
            query_result is not None
            and not query_result.empty
        ):

            st.subheader(
                "Data"
            )

            st.dataframe(

                query_result,

                use_container_width=True,

                hide_index=True
            )


        # ======================================
        # DEBUG
        # ======================================

        with st.expander(
            "Developer Details"
        ):

            st.write(
                "Analysis Type:"
            )

            st.code(
                result.get(
                    "analysis_type"
                )
            )


            st.write(
                "Generated SQL:"
            )

            st.code(

                result.get(
                    "generated_sql",
                    ""
                ),

                language="sql"
            )


            st.write(
                "Processed SQL:"
            )

            st.code(

                result.get(
                    "processed_sql",
                    ""
                ),

                language="sql"
            )


            st.write(
                "Visualization Required:"
            )

            st.code(

                str(
                    result.get(
                        "visualization_required"
                    )
                )
            )


            if result.get(
                "visualization_plan"
            ):

                st.write(
                    "Visualization Plan:"
                )

                st.json(
                    result[
                        "visualization_plan"
                    ]
                )