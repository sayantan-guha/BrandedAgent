import streamlit as st
from openai import OpenAI
import docx
from docx import Document
import io

st.title("🧠 AI Branded Content Integration Agent (OpenRouter Edition)")

# Step 1: Brand Brief Input
st.markdown("### Step 1: Enter Brand Brief")
brand = st.text_input("Brand")
product = st.text_input("Product")
integration_type = st.radio("Type of Product Integrations Needed", ["1 Active and 1 Passive", "Only Passive", "Only Active"])
communication = st.text_area("Communication (e.g. Tastes like home)")

# Step 2: Upload .docx Show Concept Files
st.markdown("### Step 2: Upload Show Concept `.docx` Files")
uploaded_files = st.file_uploader("Upload one or more `.docx` files", type="docx", accept_multiple_files=True)

# Step 3: API Key for OpenRouter
openai_api_key = st.text_input("Enter your OpenRouter API Key", type="password")

if st.button("Generate Proposal"):
    st.write("✅ Button clicked!")

    if not all([brand, product, integration_type, communication, uploaded_files, openai_api_key]):
        st.error("❌ Please fill out all fields and upload at least one file.")
    else:
        st.write("✅ All inputs valid")

        # Set up OpenRouter client using OpenAI v1 format
        client = OpenAI(
            api_key=openai_api_key,
            base_url="https://openrouter.ai/api/v1"
        )

        shows = []

        for file in uploaded_files:
            st.write(f"📄 Reading file: {file.name}")
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

        st.write("🧠 Parsed Shows:", shows)

        if not shows:
            st.error("⚠️ No shows parsed from the documents. Please check file format.")
        else:
            show = shows[0]
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

            st.write("📨 Sending to OpenRouter...")
            try:
                response = client.chat.completions.create(
                    model="mistralai/mistral-7b-instruct",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.8
                )
                st.write("✅ Got response from OpenRouter")

                result_text = response.choices[0].message.content

                proposal_doc = Document()
                proposal_doc.add_heading(f'Branded Integration Proposal for {brand}', 0)
                proposal_doc.add_paragraph(result_text)

                output_stream = io.BytesIO()
                proposal_doc.save(output_stream)
                output_stream.seek(0)

                st.success("✅ Proposal generated!")
                st.download_button(
                    label="📥 Download Proposal",
                    data=output_stream,
                    file_name=f"{brand}_integration_proposal.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            except Exception as e:
                st.error(f"❌ OpenRouter Error: {e}")
