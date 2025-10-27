import PyPDF2

def extract_skills_from_resume(resume_path):
    text = ""
    with open(resume_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()
    # Very basic skill extraction from a resume (may need improvements)
    # This looks for "Skills" section and grabs words
    text_lower = text.lower()
    if "skills" in text_lower:
        skills_section = text_lower.split("skills")[-1]
        skills_list = []
        for word in skills_section.replace('\n', ',').split(','):
            word = word.strip()
            if word:
                skills_list.append(word)
        return set(skills_list)
    else:
        # Fallback: get all unique words
        return set(text_lower.split())
