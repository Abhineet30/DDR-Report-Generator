# AI Detailed Diagnostic Report (DDR) Generator

🌟 **[Live Demo: Click Here to Test the Web App!](https://ddr-report-generator-fob4dnocwva4phvgdpcm6k.streamlit.app/)** 🌟

This project is an AI-powered logic workflow with a clean Streamlit Web UI, designed to automatically generate a structured, client-ready Detailed Diagnostic Report (DDR) by fusing data from visual property inspection and thermal reports.

## How It Works 🧠
1. **Multimodal Extraction:** The system uses `PyMuPDF` to parse both the inspection and thermal PDFs. It robustly extracts all embedded images and text separately.
2. **Context Assembly:** It compiles the textual data while simultaneously storing the images locally mapped with identifiable metadata so the AI has context for every visual.
3. **Synthesis Engine:** It passes the assembled text and mapped images directly to Google's Gemini Multimodal LLM natively.
4. **Markdown Formatting:** Gemini acts as a highly capable diagnostic engineer, reasoning through conflicts, discarding duplicate points, and generating a strictly formatted markdown report. Most importantly, it natively embeds the exact extracted images directly into the "Area-wise Observations" section to support its findings.

## Evaluation Criteria Met
* **Accuracy & Reliability:** Uses exact string extraction and image parsing, eliminating LLM hallucination of visual data. 
* **Handling Missing/Conflicting Details:** System prompt explicitly instructs the reasoning engine to state conflicts and output "Not Available" for missing fields. 
* **Logical Merging:** Leverages high-parameter multimodal logic to match thermal anomalies to corresponding visual inspection text.
* **Generalisation:** The system treats PDFs as raw data streams and isn't hardcoded to specific templates or page numbers. It will work on *any* property inspection report in PDF format. 

## Quick Start 🚀

### 1. Prerequisites
Make sure you have Python 3.9+ installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Gemini API Key
Create a `.env` file in the root directory and add your API Key:
```
GEMINI_API_KEY=your_copied_api_key_here
```
*(You can get a free key from [Google AI Studio](https://aistudio.google.com/app/apikey))*

### 4. Add Data
Place your sample reports inside the `data/` folder:
- `data/inspection_report.pdf`
- `data/thermal_report.pdf`

### 5. Run the Workflow locally!
```bash
streamlit run app.py
```

### 6. View Results
The server will open a web browser running at `http://localhost:8501`. Upload the sample PDFs from your `data/` folder and receive the automatically generated, structured final markdown DDR file directly into your UI!

## Limitations & Future Improvements
As requested by the assignment criteria, here is a transparent look at the system's current limitations and how it can be scaled.

### Current Limitations
1. **Document Structure Dependency**: The extraction engine relies on standard, digitally-created PDFs having selectable text and correctly embedded image layers. Flattened image-only PDFs (like screenshots dropped in a word doc and exported to PDF) would break the separation engine since PyMuPDF treats the whole page as a single image.
2. **Sequential Prompt Limit**: The pipeline currently passes the entire parsed text history into the Gemini context window. While Gemini 1.5/2.5 Flash has a million-token context, incredibly massive corporate reports (100+ pages) with hundreds of high-res images might eventually trigger token or payload-size limits during the API call.
3. **Image Deduplication**: PyMuPDF sometimes extracts logos, headers, or repeated UI icons as separate images, which are blindly passed to the LLM, slightly polluting the multimodal prompt.

### How I Would Improve It
1. **Pytesseract OCR Fallback**: If `PyMuPDF` detects zero textual elements on a page but finds a massive image, the system should automatically route that page through `Tesseract OCR` to physically scrape the text back out, solving the flattened PDF constraint.
2. **Vector Chunking (RAG Architecture)**: To scale this for massive 500-page enterprise datasets, I would redesign the core engine to not pass everything at once. Instead, I would chunk the observations, throw them into a local vector database (like ChromaDB), and ask the LLM to recursively build the DDR section-by-section using Retrieval-Augmented Generation (RAG).
3. **Computer Vision Object Filtering**: I would add a lightweight pre-processing model (like YOLO or OpenCV) to the `extractor.py` pipeline to detect if an extracted image is a "logo/barcode" versus an "actual property photo", deleting the junk images before they ever reach Gemini.
4. **Structured Schema Output**: Instead of returning just Markdown, I would instruct Gemini to return a structured JSON schema via `response_schema`. The backend would then automatically bind that structured data to a beautiful, printable PDF template using `WeasyPrint` or `ReportLab`.
