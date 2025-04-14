import streamlit as st
import pdfplumber
import pandas as pd
import io

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

            st.text_area("Isi Halaman Mentah:", text, height=300)

            lines = text.split("\n")
            kit_barcode = ""
            do_number = ""

            for i, line in enumerate(lines):
                if "KIT Barcode" in line:
                    kit_barcode = line.split(":")[-1].strip()
                if "parent product Code" in line and i + 1 < len(lines):
                    do_number = lines[i + 1].split("/")[-1].strip()

            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 4 and parts[0][0].isdigit():
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
        st.success("✅ Data berhasil diambil dari PDF")
        st.dataframe(df, use_container_width=True)

        st.markdown("### 📋 Tabel Teks")
        st.text_area("Copy-paste:", df.to_csv(sep="\t", index=False), height=300)

        towrite = io.BytesIO()
        df.to_excel(towrite, index=False, sheet_name="Kitting")
        towrite.seek(0)
        st.download_button("⬇️ Download Excel", towrite, file_name="kitting_list.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.warning("⚠️ Tidak ditemukan data part number yang cocok.")
