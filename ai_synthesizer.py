from google import genai
from PIL import Image
import os
from dotenv import load_dotenv

def get_gemini_client():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file. Please check your instructions on how to get one.")
    
    # Initialize the GenAI client
    return genai.Client(api_key=api_key)

def generate_ddr_report(text_data, image_paths):
    client = get_gemini_client()
    
    system_prompt = """
You are an expert property inspector and AI workflow engine.
Your task is to analyze the provided raw textual observations and extracted thermal/visual images to generate a structured Detailed Diagnostic Report (DDR).

== REQUIRED STRUCTURE ==
1. Property Issue Summary
2. Area-wise Observations
3. Probable Root Cause
4. Severity Assessment (with reasoning)
5. Recommended Actions
6. Additional Notes
7. Missing or Unclear Information

== CONTENT RULES ==
- Extract relevant observations and combine visual & thermal info logically.
- Avoid duplicate points.
- NEVER invent facts (hallucinate). Check the data carefully.
- If information conflicts between the inspection and thermal reports, mention the conflict explicitly. 
- If information is missing for a key area, explicitly write "Not Available".
- Keep formatting clean using standard Markdown.

== IMAGE RULES ==
- You have been provided with actual extracted images along with their filenames in the multimodal prompt.
- When drafting the "Area-wise Observations" section, YOU MUST embed the relevant images under the correct observation using standard markdown: `![Observation description here](images/FILENAME)`.
- Replace FILENAME with the exact filename provided to you.
- Ensure the image path precisely follows `images/the_exact_filename.jpg`.
- If an expected image is missing for an observation, explicitly mention "Image Not Available" under that observation instead of inventing a picture.
- Do not include unrelated images for the sake of it.
"""

    user_prompt = f"""
Here is the raw text from the visual inspection and thermal reports:
---
{text_data}
---

The following are the filenames of the images successfully extracted from these reports. These images are attached to this very prompt natively.
"""

    contents = [system_prompt, user_prompt]
    
    for path in image_paths:
        try:
            filename = os.path.basename(path)
            contents.append(f"Image Filename: {filename}")
            img = Image.open(path)
            contents.append(img)
        except Exception as e:
            print(f"Could not load image {path} to attach to prompt.")
            
    print(f"Sending multimodal request to Gemini API ({len(image_paths)} images attached)...")
    
    # Using Gemini 2.5 Flash / 1.5 Pro via api
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=contents
    )
    
    return response.text
