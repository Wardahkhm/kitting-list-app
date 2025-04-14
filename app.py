import streamlit as st
import pdfplumber
import pandas as pd
import io
import re

st.set_page_config(page_title="Kitting PDF Extractor", layout="wide")
st.title("📦 Kitting List PDF Extractor")

uploaded_file = st.file_uploader("Upload file PDF kitting list", type=["pdf"])

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        data = []
        no = 1

        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            st.text_area("📄 Isi Halaman Mentah", text, height=300)

            lines = text.split("\n")
            kit_barcode = ""
            do_number = ""

            # Temukan KIT BARCODE dan DO NUMBER
            for i, line in enumerate(lines):
                if "KIT Barcode" in line:
                    kit_barcode = line.split(":")[-1].strip()
                if "parent product Code" in line and i + 1 < len(lines):
                    do_line = lines[i + 1]
                    if "/" in do_line:
                        do_number = do_line.split("/")[-1].strip()

            # Ambil baris part number valid saja
            for line in lines:
                line = line.strip()
                if re.match(r"^\d{5}-\d{5,}", line):  # part number format 04064-05520 dst
                    parts = line.split()
                    if len(parts) >= 4:
                        part_number = parts[0]
                        qty = parts[-2]
                        remarks = parts[-1]
                        description = " ".join(parts[1:-2])

                        data.append([
                            no, part_number, description, qty, kit_barcode, do_number, remarks
                        ])
                        no += 1

    if data:
        df = pd.DataFrame(data, columns=["NO", "PART NUMBER", "DESCRIPTION", "@", "KIT BARCODE", "DO NUMBER", "REMARKS"])
        st.success("✅ Data berhasil diekstrak dan diformat rapi!")
        st.dataframe(df, use_container_width=True)

        st.markdown("### 📋 Tabel Siap Copy")
        st.text_area("Teks tabel:", df.to_csv(sep="\t", index=False), height=300)

        towrite = io.BytesIO()
        df.to_excel(towrite, index=False, sheet_name="Kitting")
        towrite.seek(0)
        st.download_button("⬇️ Download Excel", towrite, file_name="kitting_list.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.warning("⚠️ Tidak ditemukan data part number yang cocok.")
