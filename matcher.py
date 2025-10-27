def get_match_score(job_skills, resume_skills):
    matched = job_skills & resume_skills
    missing = job_skills - resume_skills
    score = (len(matched) / len(job_skills)) * 100 if job_skills else 0
    return matched, missing, score
