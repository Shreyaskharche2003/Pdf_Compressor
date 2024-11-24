import streamlit as st
from pathlib import Path
from io import BytesIO
import subprocess

def compress_pdf_with_levels(input_pdf: Path, output_pdf: Path, level: str) -> None:
    """Compress a PDF using Ghostscript with Low, Medium, or High levels."""
    level_mapping = {
        "low": "screen",      # Max compression, lower quality
        "medium": "ebook",    # Balanced compression and quality
        "high": "printer",    # Minimal compression, higher quality
    }
    
    if level not in level_mapping:
        raise ValueError(f"Invalid compression level: {level}")
    
    gs_level = level_mapping[level]
    
    try:
        subprocess.run(
            [
                "gs",
                "-sDEVICE=pdfwrite",
                "-dCompatibilityLevel=1.4",
                f"-dPDFSETTINGS=/{gs_level}",
                "-dNOPAUSE",
                "-dQUIET",
                "-dBATCH",
                f"-sOutputFile={output_pdf}",
                str(input_pdf),
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Ghostscript compression failed: {e}")

# Streamlit App
st.title("📄 PDF Compressor with Levels")
st.write("Upload PDF files to compress them with different levels of compression.")

# Compression level selection
compression_level = st.radio(
    "Select Compression Level",
    options=["low", "medium", "high"],
    index=1,  # Default to "medium"
)

# File uploader to accept multiple PDFs
uploaded_files = st.file_uploader("Upload PDF Files", type=["pdf"], accept_multiple_files=True)

if uploaded_files and st.button("Compress PDFs"):
    st.info("Starting compression...")

    compressed_files = []
    error_files = []

    for uploaded_file in uploaded_files:
        input_path = Path(uploaded_file.name)
        output_path = Path(f"compressed_{uploaded_file.name}")

        # Save the uploaded file to a temporary path
        input_path.write_bytes(uploaded_file.getvalue())

        try:
            st.write(f"Compressing {uploaded_file.name} with {compression_level} level...")
            compress_pdf_with_levels(input_path, output_path, compression_level)
            compressed_files.append((uploaded_file.name, output_path))
        except Exception as e:
            st.error(f"Failed to compress {uploaded_file.name}: {e}")
            error_files.append(uploaded_file.name)

    # Provide download buttons for successfully compressed files
    if compressed_files:
        st.success("Compression completed successfully!")
        for file_name, output_path in compressed_files:
            with open(output_path, "rb") as f:
                st.download_button(
                    f"Download {file_name}",
                    f.read(),
                    file_name=f"compressed_{file_name}",
                    mime="application/pdf",
                )
    # Show error messages for failed files
    if error_files:
        st.warning(f"Failed to compress the following files: {', '.join(error_files)}")
