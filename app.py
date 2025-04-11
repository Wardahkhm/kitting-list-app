import streamlit as st
import pdfplumber
import pandas as pd
import io

st.title("Kitting List PDF Extractor")
st.write("Upload PDF Kitting List")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
page_number = st.number_input("Halaman yang ingin diambil", min_value=1, step=1)

if uploaded_file and page_number:
    with pdfplumber.open(uploaded_file) as pdf:
        if page_number <= len(pdf.pages):
            page = pdf.pages[page_number - 1]  # pdfplumber uses 0-indexed pages
            text = page.extract_text()

            if text:
                lines = text.split("\n")
                data_rows = []

                for line in lines:
                    if any(char.isdigit() for char in line[:3]):  # Misalnya baris yang diawali angka adalah data
                        parts = line.split()
                        if len(parts) >= 7:
                            no = parts[0]
                            part_number = parts[1]
                            description = " ".join(parts[2:-4])
                            qty = parts[-4]
                            kit_barcode = parts[-3]
                            do_number = parts[-2]
                            remarks = parts[-1]
                            data_rows.append([no, part_number, description, qty, kit_barcode, do_number, remarks])

                df = pd.DataFrame(data_rows, columns=["NO", "PART NUMBER", "DESCRIPTION", "@", "KIT BARCODE", "DO NUMBER", "REMARKS"])
                st.dataframe(df)

                # Download button
                towrite = io.BytesIO()
                df.to_excel(towrite, index=False, sheet_name='Kitting List')
                towrite.seek(0)
                st.download_button("Download Excel", towrite, file_name="kitting_list.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                st.warning("Teks tidak ditemukan di halaman tersebut.")
        else:
            st.error("Halaman tidak ada di file PDF.")
