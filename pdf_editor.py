import streamlit as st
import PyPDF2
import pdfplumber
import fitz  # PyMuPDF
import os
import io

# Page setup
st.set_page_config(page_title="PDF Editor", page_icon="📄", layout="wide")

# Title
st.title("📄 PDF Editor")

# Create tabs for each function
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔗 Merge PDFs",
    "✂️ Split PDF",
    "📝 Extract Text",
    "🖼️ Extract Images",
    "🔐 Encrypt PDF"
])

# ======================== TAB 1: MERGE ========================
with tab1:
    st.subheader("Merge Multiple PDFs")
    
    uploaded_files = st.file_uploader(
        "Upload PDF files to merge",
        accept_multiple_files=True,
        type="pdf"
    )
    
    if uploaded_files:
        st.write(f"✅ {len(uploaded_files)} file(s) selected")
        
        if st.button("Merge PDFs", key="merge"):
            try:
                pdf_writer = PyPDF2.PdfWriter()
                
                for uploaded_file in uploaded_files:
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    for page in pdf_reader.pages:
                        pdf_writer.add_page(page)
                
                output = io.BytesIO()
                pdf_writer.write(output)
                output.seek(0)
                
                st.success("✅ PDFs merged successfully!")
                
                st.download_button(
                    label="Download Merged PDF",
                    data=output.getvalue(),
                    file_name="merged.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ======================== TAB 2: SPLIT ========================
with tab2:
    st.subheader("Split PDF into Parts")
    
    uploaded_file = st.file_uploader("Upload PDF to split", type="pdf", key="split_file")
    
    if uploaded_file:
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            total_pages = len(pdf_reader.pages)
            
            st.info(f"📊 Total pages: {total_pages}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                num_parts = st.number_input(
                    "How many parts?",
                    min_value=2,
                    max_value=total_pages,
                    value=2
                )
            
            # Split points
            split_points = []
            st.write(f"Define page ranges for {num_parts} parts:")
            
            for i in range(num_parts):
                col1, col2 = st.columns(2)
                with col1:
                    start = st.number_input(
                        f"Part {i+1} - Start page",
                        min_value=1,
                        max_value=total_pages,
                        value=1 if i == 0 else 2,
                        key=f"start_{i}"
                    )
                with col2:
                    end = st.number_input(
                        f"Part {i+1} - End page",
                        min_value=1,
                        max_value=total_pages,
                        value=total_pages if i == num_parts-1 else 2,
                        key=f"end_{i}"
                    )
                
                if start <= end:
                    split_points.append((start, end))
            
            if st.button("Split PDF", key="split_btn"):
                try:
                    output_files = []
                    
                    for part_num, (start, end) in enumerate(split_points):
                        writer = PyPDF2.PdfWriter()
                        
                        for page_num in range(start - 1, end):
                            writer.add_page(pdf_reader.pages[page_num])
                        
                        output = io.BytesIO()
                        writer.write(output)
                        output.seek(0)
                        output_files.append(output.getvalue())
                    
                    st.success("✅ PDF split successfully!")
                    
                    for idx, file_data in enumerate(output_files):
                        st.download_button(
                            label=f"Download Part {idx + 1}",
                            data=file_data,
                            file_name=f"part_{idx + 1}.pdf",
                            mime="application/pdf"
                        )
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        except Exception as e:
            st.error(f"❌ Error reading PDF: {e}")

# ======================== TAB 3: EXTRACT TEXT ========================
with tab3:
    st.subheader("Extract Text from PDF")
    
    uploaded_file = st.file_uploader("Upload PDF", type="pdf", key="text_file")
    
    if uploaded_file:
        if st.button("Extract Text", key="extract_text"):
            try:
                with pdfplumber.open(uploaded_file) as pdf:
                    full_text = ""
                    for page_num, page in enumerate(pdf.pages, 1):
                        text = page.extract_text()
                        if text:
                            full_text += f"\n--- Page {page_num} ---\n{text}"
                
                if full_text.strip():
                    st.success("✅ Text extracted!")
                    
                    st.text_area(
                        "Extracted Text",
                        value=full_text,
                        height=300
                    )
                    
                    st.download_button(
                        label="Download as Text File",
                        data=full_text,
                        file_name="extracted_text.txt",
                        mime="text/plain"
                    )
                else:
                    st.warning("⚠️ No text found (might be scanned image)")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ======================== TAB 4: EXTRACT IMAGES ========================
with tab4:
    st.subheader("Extract Images from PDF")
    
    uploaded_file = st.file_uploader("Upload PDF", type="pdf", key="images_file")
    
    if uploaded_file:
        if st.button("Extract Images", key="extract_images"):
            try:
                pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                extracted_images = []
                
                for page_index, page in enumerate(pdf_document):
                    image_list = page.get_images(full=True)
                    
                    for img_index, img in enumerate(image_list):
                        xref = img[0]
                        base_image = pdf_document.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        
                        extracted_images.append({
                            "bytes": image_bytes,
                            "ext": image_ext,
                            "page": page_index + 1,
                            "index": img_index + 1
                        })
                
                pdf_document.close()
                
                if extracted_images:
                    st.success(f"✅ Found {len(extracted_images)} image(s)!")
                    
                    cols = st.columns(3)
                    for idx, img_data in enumerate(extracted_images):
                        with cols[idx % 3]:
                            st.image(img_data["bytes"], caption=f"Page {img_data['page']}")
                            st.download_button(
                                label="Download",
                                data=img_data["bytes"],
                                file_name=f"image_p{img_data['page']}_i{img_data['index']}.{img_data['ext']}",
                                mime=f"image/{img_data['ext']}",
                                key=f"img_{idx}"
                            )
                else:
                    st.warning("⚠️ No images found")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ======================== TAB 5: ENCRYPT ========================
with tab5:
    st.subheader("Encrypt PDF with Password")
    
    uploaded_file = st.file_uploader("Upload PDF", type="pdf", key="encrypt_file")
    
    password = st.text_input("Enter password", type="password")
    password_confirm = st.text_input("Confirm password", type="password")
    
    if uploaded_file and password:
        if password != password_confirm:
            st.error("❌ Passwords don't match!")
        elif len(password) < 4:
            st.error("❌ Password must be at least 4 characters!")
        else:
            if st.button("Encrypt PDF", key="encrypt_btn"):
                try:
                    reader = PyPDF2.PdfReader(uploaded_file)
                    writer = PyPDF2.PdfWriter()
                    
                    for page in reader.pages:
                        writer.add_page(page)
                    
                    writer.encrypt(password)
                    
                    output = io.BytesIO()
                    writer.write(output)
                    output.seek(0)
                    
                    st.success("✅ PDF encrypted!")
                    
                    st.download_button(
                        label="Download Encrypted PDF",
                        data=output.getvalue(),
                        file_name="encrypted.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"❌ Error: {e}")

st.divider()
st.info("💡 Tip: All operations happen locally on your computer. No files are uploaded to any server!")
