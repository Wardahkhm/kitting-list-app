
import streamlit as st
import pdfplumber
import pandas as pd
import io

st.title("Kitting List PDF Extractor 📄➡️📊")

uploaded_file = st.file_uploader("Upload PDF Kitting List", type="pdf")

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        all_text = ""
        for page in pdf.pages:
            all_text += page.extract_text() + "\n"

    # Coba ekstrak jadi tabel (sederhana)
    rows = [line.split() for line in all_text.split("\n") if line.strip()]
    df = pd.DataFrame(rows)

    st.subheader("📋 Tabel dari PDF")
    st.dataframe(df)

    # Download sebagai Excel
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False, header=False)
    st.download_button(
        label="Download sebagai Excel",
        data=excel_buffer,
        file_name="kitting_list.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
