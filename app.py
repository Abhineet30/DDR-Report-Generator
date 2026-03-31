import streamlit as st
import os
import re
import base64
from dotenv import load_dotenv
from extractor import extract_content_from_pdf
from ai_synthesizer import generate_ddr_report

st.set_page_config(page_title="AI DDR Generator", page_icon="🏢", layout="wide")

def embed_images_as_base64(markdown_text, images_dir):
    """Converts standard markdown image links into embedded base64 strings so Streamlit can render them natively"""
    def replacer(match):
        alt_text = match.group(1)
        filepath = match.group(2)
        # We know filepath is like 'images/filename.jpg'
        filename = os.path.basename(filepath)
        full_path = os.path.join(images_dir, filename)
        
        if os.path.exists(full_path):
            with open(full_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
                ext = filename.split(".")[-1].lower()
                mime_type = "image/png" if ext == "png" else "image/jpeg"
                return f"![{alt_text}](data:{mime_type};base64,{encoded_string})"
        # If file not found, explicitly show "Image Not Available" text instead of a broken generic markdown icon
        return f"**[⚠️ Image Not Available: {alt_text}]**"
        
    pattern = r"\!\[([^\]]*)\]\((images/[^\)]+)\)"
    return re.sub(pattern, replacer, markdown_text)

def main():
    st.title("🏗️ Applied AI Builder: DDR Generator")
    st.write("Convert raw Inspection & Thermal PDF Reports into structured, client-ready markdown deliverables through the power of multimodal AI.")
    
    # Init directories
    input_dir = "data/streamlit_uploads"
    output_dir = "output"
    images_dir = os.path.join(output_dir, "images")
    for d in [input_dir, output_dir, images_dir]:
        os.makedirs(d, exist_ok=True)
    
    # Sidebar
    st.sidebar.header("Configuration")
    
    # Load API Key from .env securely
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY", "")
    
    st.sidebar.warning("Note: The model takes 15-30 seconds to run because it parses heavy image files and performs rigorous contextual reasoning.")

    # Main UI
    col1, col2 = st.columns(2)
    with col1:
        inspection_file = st.file_uploader("Upload Inspection Report (PDF)", type=["pdf"])
    with col2:
        thermal_file = st.file_uploader("Upload Thermal Report (PDF)", type=["pdf"])
        
    if st.button("Generate Diagnostic Report (DDR)", type="primary"):
        if not api_key:
            st.error("Please add your Gemini API Key to your completely hidden `.env` file first.")
            return
            
        if inspection_file and thermal_file:
            with st.spinner("Step 1/2: Extracting raw text and images from PDFs..."):
                # Save uploaded files temporarily
                insp_path = os.path.join(input_dir, "inspection_upload.pdf")
                therm_path = os.path.join(input_dir, "thermal_upload.pdf")
                
                with open(insp_path, "wb") as f:
                    f.write(inspection_file.getbuffer())
                with open(therm_path, "wb") as f:
                    f.write(thermal_file.getbuffer())
                    
                # Extract
                insp_text, insp_images = extract_content_from_pdf(insp_path, "Inspection", images_dir)
                therm_text, therm_images = extract_content_from_pdf(therm_path, "Thermal", images_dir)
                
                combined_text = insp_text + "\n\n" + therm_text
                all_images = insp_images + therm_images
            
            with st.spinner(f"Step 2/2: Prompting Gemini Multimodal with {len(all_images)} extracted images. This takes ~30 seconds..."):
                try:
                    report_markdown = generate_ddr_report(combined_text, all_images)
                    if report_markdown:
                        # Process markdown to show images in streamlit natively
                        rendered_md = embed_images_as_base64(report_markdown, images_dir)
                        
                        st.success("✅ DDR Generated Successfully!")
                        st.markdown("---")
                        # Display
                        st.markdown(rendered_md, unsafe_allow_html=True)
                        
                        # Provide download link
                        st.markdown("---")
                        st.download_button(
                            label="📥 Download Full Markdown Report",
                            data=report_markdown,
                            file_name="Final_DDR_Report.md",
                            mime="text/markdown"
                        )
                    else:
                        st.error("Gemini failed to return a string. Please check the logs.")
                except Exception as e:
                    st.error(f"Error communicating with Gemini: {e}")
                    
        else:
            st.warning("Please upload both the Inspection and Thermal PDFs to continue.")

if __name__ == "__main__":
    main()
