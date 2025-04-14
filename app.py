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
            st.text_area("Isi Halaman Mentah:", text, height=400)
            if not text:
                continue

            # Cari KIT BARCODE dan DO NUMBER
            kit_barcode_match = re.search(r"KIT Barcode:\s*(\d+)", text)
            do_number_match = re.search(r"parent product Code\n(.+?/F\d+)", text)

            kit_barcode = kit_barcode_match.group(1) if kit_barcode_match else ""
            do_number = do_number_match.group(1).split("/")[-1] if do_number_match else ""

            # Ambil baris part
            lines = text.split("\n")
            for line in lines:
                line = line.strip()
                # Match pola: PARTNUMBER QTYDESCRIPTION REMARKS
                match = re.match(r"^([0-9\-]+)\s+(\d+)([A-Z ]+)([A-Z0-9/\\-]+)$", line)
                if match:
                    part_number = match.group(1)
                    qty = match.group(2)
                    description = match.group(3).strip()
                    remarks = match.group(4).strip()

                    data.append([
                        no, part_number, description, qty, kit_barcode, do_number, remarks
                    ])
                    no += 1

    if data:
        df = pd.DataFrame(data, columns=["NO", "PART NUMBER", "DESCRIPTION", "@", "KIT BARCODE", "DO NUMBER", "REMARKS"])
        st.success("✅ Data berhasil diambil dari PDF")
        st.dataframe(df, use_container_width=True)

        # Text area buat copy
        st.markdown("### 📋 Tabel Siap Copy")
        st.text_area("Tabel teks:", df.to_csv(sep="\t", index=False), height=300)

        # Download button
        towrite = io.BytesIO()
        df.to_excel(towrite, index=False, sheet_name="Kitting")
        towrite.seek(0)
        st.download_button("⬇️ Download Excel", towrite, file_name="kitting_list.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.warning("⚠️ Tidak ditemukan data part number yang cocok.")
