import streamlit as st
from openai import OpenAI
import docx
from docx import Document
import io

st.title("🧠 AI Branded Content Integration Agent (OpenRouter with Claude Fallback)")

# Step 1: Brand Brief Input
st.markdown("### Step 1: Enter Brand Brief")
brand = st.text_input("Brand")
product = st.text_input("Product")
communication = st.text_area("Communication (e.g. Tastes like home)")

# Step 1.1: Number of Integration Types
st.markdown("### Step 1.1: Number of Integrations Per Show")
num_active = st.number_input("Active Integrations", min_value=0, max_value=5, value=1, step=1)
num_passive = st.number_input("Passive Integrations", min_value=0, max_value=5, value=1, step=1)
num_hyperactive = st.number_input("Hyperactive Integrations", min_value=0, max_value=5, value=0, step=1)

# Step 2: Upload .docx Show Concept Files
st.markdown("### Step 2: Upload Show Concept `.docx` Files")
uploaded_files = st.file_uploader("Upload one or more `.docx` files", type="docx", accept_multiple_files=True)

# Step 3: API Key for OpenRouter
openai_api_key = st.text_input("Enter your OpenRouter API Key", type="password")

if st.button("Generate Proposal"):
    st.write("✅ Button clicked!")

    if not all([brand, product, communication, uploaded_files, openai_api_key]):
        st.error("❌ Please fill out all fields and upload at least one file.")
    else:
        st.write("✅ All inputs valid")

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
            proposal_doc = Document()
            proposal_doc.add_heading(f'Branded Integration Proposal for {brand}', 0)

            for show in shows:
                prompt = f"""
You are a creative screenwriter tasked with integrating a product into a show in a natural, cinematic way.

Show Details:
- Show Name: {show['Show Name']}
- Themes: {show['Themes']}
- Episodes: {', '.join(show['Episodes'][:2])}

Brand Brief:
- Brand: {brand}
- Product: {product}
- Communication: {communication}

Integration Needs (target count per show):
- {num_active} Active Integrations
- {num_passive} Passive Integrations
- {num_hyperactive} Hyperactive Integrations

🧠 Important:
Only write integrations that feel natural to the story, setting, and characters.
If the product doesn't fit organically into a scene type, say:
> “No suitable [Active/Passive/Hyperactive] integration found for this show without it feeling forced.”

Be honest. This proposal will be reviewed by a brand team — transparency is valued over quantity.

Write each scene in screenplay tone (200–300 words), grouped under:
1. Active Integration Scene(s)
2. Passive Integration Scene(s)
3. Hyperactive Integration Scene(s) (if any)
"""

                try:
                    st.write(f"🧠 Generating for '{show['Show Name']}' using Claude 3 Sonnet...")
                    response = client.chat.completions.create(
                        model="anthropic/claude-3-sonnet",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.8
                    )
                    model_used = "Claude 3 Sonnet"
                    result_text = response.choices[0].message.content

                except Exception as e:
                    st.warning(f"⚠️ Claude 3 failed for '{show['Show Name']}' — falling back to Mistral 7B.")
                    try:
                        response = client.chat.completions.create(
                            model="mistralai/mistral-7b-instruct",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.8
                        )
                        model_used = "Mistral 7B"
                        result_text = response.choices[0].message.content
                    except Exception as e2:
                        st.error(f"❌ Failed with both models for '{show['Show Name']}': {e2}")
                        continue

                proposal_doc.add_heading(f"{show['Show Name']} (via {model_used})", level=2)
                proposal_doc.add_paragraph(result_text)
                proposal_doc.add_paragraph("\n" + "-" * 50 + "\n")

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
