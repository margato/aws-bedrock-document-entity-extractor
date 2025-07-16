from dotenv import load_dotenv
load_dotenv()

from time import time
import streamlit as st
import llm


def render_page():
    st.set_page_config(page_title="Document Entity Extractor") 
    st.title("Document Entity Extractor")
    st.text("AWS Bedrock PoC")
    st.markdown(
        """
        <style>
        .stMainBlockContainer {
            max-width: 95% !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    left_col, right_col = st.columns(2)

    with left_col:
        uploaded_file = st.file_uploader("Upload document (PDF, PNG, JPG, etc.)", type=["pdf", "png", "jpg", "jpeg"])
        st.divider()
        st.markdown("### Enter extraction fields")
        extraction_fields = []
        context = st.text_input(f"Document Context", key=f"doc_context")
        num_entities = st.number_input("How many entities to extract?", min_value=1, max_value=20, step=1)
        for i in range(num_entities):
            col1, col2 = st.columns(2)
            with col1:
                key = st.text_input(f"Key", key=f"key_{i}")
            with col2:
                desc = st.text_input(f"Description", key=f"desc_{i}")
            extraction_fields.append({"key": key.strip(), "description": desc.strip()})

    with right_col:
        st.markdown("##### Result")
        run_clicked = st.button("Extract data")
        if 'run_clicked' in locals() and run_clicked:
            if not uploaded_file:
                st.error("Please upload a document.")
            else:
                for idx, field in enumerate(extraction_fields):
                    if not field['key'] or not field['description']:
                        st.error(f"Row {idx+1} must be filled.")
                        return
                start_time = time()
                with st.spinner("Calling AWS Bedrock to extract entities..."):
                    document_bytes = uploaded_file.read()
                    results = llm.call_agent(context, document_bytes, uploaded_file.type, extraction_fields)
                elapsed = time() - start_time
                st.success(f"Execution completed in {elapsed:.2f} seconds.")
                st.json(results)


if __name__ == "__main__":
    render_page()
