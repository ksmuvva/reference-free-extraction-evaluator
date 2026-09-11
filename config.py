import os

JUDGE_MODEL = os.getenv("JUDGE_MODEL", "openai/gpt-5.6")

FIELD_DEFINITIONS = {
    "reason_for_claim": "Reasons the applicant gives for claiming asylum, including fears, threats, persecution, relevant events, actors, motives and reasons they cannot safely return.",
    "medical_conditions": "Medical or health conditions belonging specifically to the applicant. Do not attribute another person's condition to the applicant.",
    "family_relationships": "Explicitly stated family relationships relevant to the applicant, including spouse/partner, children, parents, siblings and other relatives.",
    "countries_travelled": "Countries the applicant personally travelled through or stayed in. Do not infer travel from nationality or another person's movements.",
}

OUTPUT_SCHEMA = {
    "reason_for_claim": str,
    "medical_conditions": list,
    "family_relationships": str,
    "countries_travelled": list,
}

PASS_COVERAGE = float(os.getenv("PASS_COVERAGE", "0.90"))
WARN_COVERAGE = float(os.getenv("WARN_COVERAGE", "0.75"))
PASS_FIELD_ALIGNMENT = float(os.getenv("PASS_FIELD_ALIGNMENT", "1.0"))
WARN_FIELD_ALIGNMENT = float(os.getenv("WARN_FIELD_ALIGNMENT", "0.90"))
