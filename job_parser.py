def extract_skills_from_job_desc(desc):
    # Assume comma-separated skills or keywords
    return set(word.strip().lower() for word in desc.split(",") if word.strip())
