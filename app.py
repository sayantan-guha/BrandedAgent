import streamlit as st
import docx
import openai
from docx import Document
import io
from openai import OpenAI

st.title("🧠 AI Branded Content Integration Agent")

st.markdown("### Step 1: Enter Brand Brief")
brand = st.text_input("Brand")
product = st.text_input("Product")
integration_type = st.radio("Type of Product Integrations Needed", ["1 Active and 1 Passive", "Only Passive", "Only Active"])
communication = st.text_area("Communication (e.g. Tastes like home)")

st.markdown("### Step 2: Upload Show Concept `.docx` Files")
uploaded_files = st.file_uploader("Upload one or more `.docx` files", type="docx", accept_multiple_files=True)

openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")

if st.button("Generate Proposal"):
    if not all([brand, product, integration_type, communication, uploaded_files, openai_api_key]):
        st.error("Please fill out all fields and upload at least one file.")
    else:
        openai.api_key = openai_api_key

        shows = []

        for file in uploaded_files:
            doc = docx.Document(file)
            content = {"Show Name": "", "Themes": "", "Episodes": []}
            for para in doc.paragraphs:
                text = para.text.strip()
                if text.startswith("Show Name-"):
                    content["Show Name"] = text.replace("Show Name-", "").strip()
                elif text.startswith("Themes-"):
                    content["Themes"] = text.replace("Themes-", "").strip()
                elif text.startswith("Episode"):
                    content["Episodes"].append(text)
            shows.append(content)

        proposal_doc = Document()
        proposal_doc.add_heading(f'Branded Integration Proposal for {brand}', 0)

        for show in shows:
            prompt = f"""
You are a creative screenwriter. Given this show:

Show Name: {show['Show Name']}
Themes: {show['Themes']}
Episodes: {', '.join(show['Episodes'][:2])}

And this brand brief:
Brand: {brand}
Product: {product}
Integration Type: {integration_type}
Communication: {communication}

Suggest one cinematic **Active Integration Scene** and one **Passive Integration Scene** for the show. 
Make sure the active scene aligns with the brand communication emotionally. 
Write both scenes in a screenplay-like tone (200-300 words each).

Start with a title like:
"Show: {show['Show Name']}"
Then two sections:
1. Active Integration Scene
2. Passive Integration Scene
"""
client = openai.OpenAI(api_key=openai_api_key)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.8
)

result_text = response.choices[0].message.content
            proposal_doc.add_paragraph(result_text)
            proposal_doc.add_paragraph("\n" + "-" * 50 + "\n")

        output_stream = io.BytesIO()
        proposal_doc.save(output_stream)
        output_stream.seek(0)

        st.success("Proposal generated!")
        st.download_button(
            label="📥 Download Proposal",
            data=output_stream,
            file_name=f"{brand}_integration_proposal.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
