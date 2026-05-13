# model/subjects.py
# (MODEL)

from typing import List


def subjects_for(strand: str, grade: str) -> List[str]:
    """
    Returns the hardcoded subject list based on the student's
    Academic Strand and Grade Level.
    """
    strand = (strand or "").upper().strip()
    grade = str(grade).strip()

    # --- ABM STRAND ---
    if strand == "ABM":
        if grade == "11":
            return ["Organization & Management", "Marketing", "Applied Economics", "Business Math", "Fundamentals of ABM 1"]
        if grade == "12":
            return ["Business Finance", "Business Ethics", "Fundamentals of ABM 2", "Entrepreneurship", "Business Simulation"]

    # --- STEM STRAND ---
    if strand == "STEM":
        if grade == "11":
            return ["Pre-Calculus", "General Chemistry 1", "Earth Science", "General Biology 1", "General Physics 1"]
        if grade == "12":
            return ["Basic Calculus", "General Chemistry 2", "General Biology 2", "General Physics 2", "Research/Capstone"]

    # --- HUMSS STRAND ---
    if strand == "HUMSS":
        if grade == "11":
            return ["Creative Writing", "Introduction to World Religions", "Philippine Politics and Governance", "Disciplines in Social Sciences", "Creative Nonfiction"]
        if grade == "12":
            # Note: HUMSS 12 subjects are now correctly mapped
            return ["Trends, Networks, and Critical Thinking", "Community Engagement", "Disciplines and Ideas in the Applied Social Sciences", "Philippine Politics", "Research Project"]

    # --- GAS STRAND ---
    if strand == "GAS":
        if grade == "11":
            return ["Applied Economics", "Organization and Management", "Humanities 1", "Social Science 1", "Disaster Readiness"]
        if grade == "12":
            return ["Trends, Networks, and Critical Thinking", "Community Engagement", "Humanities 2", "Social Science 2", "Research Project"]

    # --- TVL STRAND ---
    if strand == "TVL":
        # General technical subjects; can be specialized further if needed
        if grade == "11":
            return ["Computer Programming 1", "Animation", "Computer Systems Servicing", "Technical Drafting", "Empowerment Technologies"]
        if grade == "12":
            return ["Computer Programming 2", "Work Immersion", "Information and Communications Technology", "Entrepreneurship", "Research Project"]

    # default fallback if no strand matches (now acts as a safety net)
    return ["General Mathematics", "Oral Communication", "Physical Education", "Understanding Culture", "Personal Development"]