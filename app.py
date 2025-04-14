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

            # Cek isi mentah untuk debugging
            st.text_area("Isi Halaman Mentah:", text, height=300)

            # Cari KIT BARCODE dan DO NUMBER
            kit_barcode_match = re.search(r"KIT Barcode:\s*(\d+)", text)
            do_number_match = re.search(r"parent product Code\n(.+?/F\d+)", text)

            kit_barcode = kit_barcode_match.group(1) if kit_barcode_match else ""
            do_number = do_number_match.group(1).split("/")[-1] if do_number_match else ""

            lines = text.split("\n")
            for line in lines:
                # Cek baris seperti: PARTNUMBER DESCRIPTION QTY REMARKS
                match = re.match(r"^([0-9\-]+)\s+([A-Z \-]+?)\s+(\d+)\s+([A-Z0-9/\-]+)$", line.strip())
                if match:
                    part_number = match.group(1)
                    description = match.group(2).strip()
                    qty = match.group(3)
                    remarks = match.group(4)

                    data.append([
                        no, part_number, description, qty, kit_barcode, do_number, remarks
                    ])
                    no += 1

    if data:
        df = pd.DataFrame(data, columns=["NO", "PART NUMBER", "DESCRIPTION", "@", "KIT BARCODE", "DO NUMBER", "REMARKS"])
        st.success("✅ Data berhasil diambil dari PDF")
        st.dataframe(df, use_container_width=True)

        # Tabel teks siap copy
        st.markdown("### 📋 Tabel Teks")
        st.text_area("Copy-paste:", df.to_csv(sep="\t", index=False), height=300)

        # Download Excel
        towrite = io.BytesIO()
        df.to_excel(towrite, index=False, sheet_name="Kitting")
        towrite.seek(0)
        st.download_button("⬇️ Download Excel", towrite, file_name="kitting_list.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.warning("⚠️ Tidak ditemukan data part number yang cocok.")
