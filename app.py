import streamlit as st
import pandas as pd
import io
import PyPDF2
import string

# Extract text from PDF file function
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text

# Parse skills and weights from separate input fields
def parse_weights(skills_str, weights_str):
    skills = [s.strip().lower() for s in skills_str.split(",") if s.strip()]
    weights_raw = [w.strip() for w in weights_str.split(",")]
    weights = []
    for w in weights_raw:
        try:
            weights.append(float(w))
        except:
            weights.append(1.0)
    while len(weights) < len(skills):
        weights.append(1.0)
    return dict(zip(skills, weights))

# Page setup
st.set_page_config(layout="wide", page_title="Resume Screener Pro", page_icon="📄")

# Custom CSS for styling
st.markdown("""
<style>
    .ranked-box {
        border: 3px solid #3762F0;
        background: linear-gradient(to right, #dee2e6, #f8f9fa);
        border-radius: 14px;
        padding: 20px;
        font-family: Arial, sans-serif;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 30px;
        animation: pulse 2s infinite alternate;
        color: #000000;  /* Make all text black */
    }
    @keyframes pulse {
        from { box-shadow: 0 0 8px #a0c1f7; }
        to { box-shadow: 0 0 20px #3762F0; }
    }
    .res-card {
        background-color: #fff;
        padding: 15px;
        margin: 8px;
        border-radius: 12px;
        box-shadow: 1px 2px 10px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .res-card:hover {
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        transform: translateY(-3px);
    }
    .res-card h4, .res-card p {
        color: #222;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>Resume Screener Pro</h1>", unsafe_allow_html=True)
st.markdown("<p>Upload multiple resumes and assign weights to skills for weighted compatibility scores.</p>", unsafe_allow_html=True)
st.markdown("---")

# Layout columns
col_left, col_right = st.columns([1, 2])

with col_left:
    st.header("Input Job Skills & Weights")
    skills_text = st.text_area("Skills (comma separated)", value="Python, SQL, web development", height=100)
    weights_text = st.text_area("Weights (comma separated) for each skill", value="5, 3, 4", height=100)
    uploaded_files = st.file_uploader("Upload PDFs", type='pdf', accept_multiple_files=True)
    ranked_placeholder = st.empty()

if uploaded_files and skills_text and weights_text:
    skill_weights = parse_weights(skills_text, weights_text)
    job_skills = list(skill_weights.keys())

    results = []
    for uploaded_file in uploaded_files:
        resume_text = extract_text_from_pdf(uploaded_file)
        matched = []
        matched_points = 0
        missing = []

        for skill in job_skills:
            if skill in resume_text:
                matched.append(skill)
                matched_points += skill_weights.get(skill, 1)
            else:
                missing.append(skill)

        total_points = sum(skill_weights.values())
        score = (matched_points / total_points) * 100 if total_points else 0

        results.append({
            "name": uploaded_file.name,
            "score": score,
            "matched": matched,
            "missing": missing
        })

    ranked = sorted(results, key=lambda x: x["score"], reverse=True)

    # Render ranked list inside styled box with black text
    ranked_content = "<h3>Ranked List</h3>"
    for idx, res in enumerate(ranked, 1):
        ranked_content += f"<p><b>{idx}. {res['name']}</b> — Score: {res['score']:.2f}%, Matched: {', '.join(res['matched']) if res['matched'] else 'None'}</p>"
    ranked_placeholder.markdown(f"<div class='ranked-box'>{ranked_content}</div>", unsafe_allow_html=True)

    # Prepare CSV for download
    df_ranking = pd.DataFrame(ranked)
    df_ranking['matched'] = df_ranking['matched'].apply(lambda x: ', '.join(x))
    df_ranking['missing'] = df_ranking['missing'].apply(lambda x: ', '.join(x))
    csv_data = df_ranking.to_csv(index=False)

    # Download button below ranked list
    ranked_placeholder.download_button("Download Ranked List as CSV", data=csv_data, file_name='ranked_list.csv', mime='text/csv')

    # Display resume cards horizontally on the right
    cols_cards = col_right.columns(len(ranked))
    for i, res in enumerate(ranked):
        with cols_cards[i]:
            st.markdown(f"""
            <div class='res-card'>
                <h4>{res['name']}</h4>
                <p><b>Score:</b> {res['score']:.2f}%</p>
                <p><b>Matched Skills:</b> {', '.join(res['matched']) if res['matched'] else 'None'}</p>
                <p><b>Missing Skills:</b> {', '.join(res['missing']) if res['missing'] else 'None'}</p>
            </div>""", unsafe_allow_html=True)

else:
    with col_left:
        st.info("Please provide skills, weights, and upload at least one resume.")
