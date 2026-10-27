import re
import requests

def check_text_is_biomedical(sample_text):
    text_lower = sample_text.lower()

    non_biomed_indicators = [
        r"\bsoftware\s+engineering\b",
        r"\bweb\s+application\b",
        r"\bfrontend\b",
        r"\bbackend\b",
        r"\bfull\s*stack\b",
        r"\breact(\.js)?\b",
        r"\bnode(\.js)?\b",
        r"\bgithub\b",
        r"\bsource\s+code\b",
        r"\bdatabase\s+management\b",
        r"\bcompiler\b",
        r"\boperating\s+system\b",
        r"\bmachine\s+learning\s+project\b",
        r"\bdeep\s+learning\s+project\b",
        r"\bproject\s+report\b",
        r"\bproject\s+synopsis\b",
        r"\bsynopsis\s+of\b",
        r"\bsubmitted\s+in\s+partial\s+fulfill?ment\b",
        r"\bdepartment\s+of\s+computer\s+science\b",
        r"\bdepartment\s+of\s+information\s+technology\b",
        r"\bdepartment\s+of\s+mechanical\b",
        r"\bdepartment\s+of\s+civil\b",
        r"\bdepartment\s+of\s+electrical\b",
        r"\bbachelor\s+of\s+technology\b",
        r"\bbachelor\s+of\s+engineering\b",
        r"\bmaster\s+of\s+computer\b",
        r"\bmaster\s+of\s+technology\b",
        r"\bb\.?tech\b",
        r"\bm\.?tech\b",
        r"\bb\.?e\.?\b",
        r"\bm\.?c\.?a\.?\b",
        r"\broll\s+no\b",
        r"\bacademics?\s+year\b",
        r"\bcourse\s+syllabus\b",
        r"\bsemester\s+project\b",
        r"\bfaculty\s+guide\b",
        r"\bproject\s+guide\b",
        r"\bsports\s+analytics\b",
        r"\bcricket\b",
        r"\bfootball\b",
        r"\bsoccer\b",
        r"\bbasketball\b",
        r"\bnba\b",
        r"\bipl\b",
        r"\bpremier\s+league\b",
        r"\bmatch\s+prediction\b",
        r"\bplayer\s+performance\b",
        r"\bbatting\s+average\b",
        r"\bbowling\b",
        r"\bebitda\b",
        r"\bfinancial\s+budget\b",
        r"\bbalance\s+sheet\b",
        r"\bquarterly\s+revenue\b",
        r"\bstock\s+market\b",
        r"\bcryptocurrency\b",
        r"\bventure\s+capital\b"
    ]
    matched_negatives = [p for p in non_biomed_indicators if re.search(p, text_lower)]

    trial_design_patterns = [
        r"\bclinical\s+trial\b",
        r"\brandomized\s+controlled\s+trial\b",
        r"\brandomised\s+controlled\s+trial\b",
        r"\bdouble-blind\b",
        r"\bopen-label\b",
        r"\bplacebo-controlled\b",
        r"\bphase\s+[1-4]\b",
        r"\bclinicaltrials\.gov\b",
        r"\btrial\s+registry\b",
        r"\binclusion\s+criteria\b",
        r"\bexclusion\s+criteria\b",
        r"\bconsort\b",
        r"\bsystematic\s+review\b",
        r"\bmeta-analysis\b",
        r"\bmeta\s+analysis\b"
    ]
    matched_trial_design = [p for p in trial_design_patterns if re.search(p, text_lower)]

    patient_cohort_patterns = [
        r"\bpatient\s+cohort\b",
        r"\bclinical\s+cohort\b",
        r"\bhospitalized\s+patients\b",
        r"\binpatients?\b",
        r"\boutpatients?\b",
        r"\bpediatric\s+patients\b",
        r"\belderly\s+patients\b",
        r"\bhuman\s+subjects\b",
        r"\bhealthy\s+volunteers\b",
        r"\bpatients\s+with\b",
        r"\bmorbidity\b",
        r"\bmortality\s+rate\b",
        r"\badverse\s+events?\b"
    ]
    matched_cohorts = [p for p in patient_cohort_patterns if re.search(p, text_lower)]

    drug_intervention_patterns = [
        r"\bpharmacokinetics\b",
        r"\bpharmacodynamics\b",
        r"\bdosage\s+regimen\b",
        r"\bdrug\s+administration\b",
        r"\bcombination\s+therapy\b",
        r"\bmonotherapy\b",
        r"\btolerability\b",
        r"\btherapeutic\s+efficacy\b",
        r"\binhibitor\b",
        r"\bagonist\b",
        r"\bantagonist\b",
        r"\bsglt2\b",
        r"\bglp-?1\b",
        r"\binsulin\b",
        r"\bantidiabetic\b",
        r"\bantimicrobial\b",
        r"\bantibiotic\b",
        r"\bchemotherapy\b"
    ]
    matched_drugs = [p for p in drug_intervention_patterns if re.search(p, text_lower)]

    metric_patterns = [
        r"\bhazard\s+ratio\b",
        r"\bodds\s+ratio\b",
        r"\brelative\s+risk\b",
        r"\boverall\s+survival\b",
        r"\bprogression-free\s+survival\b",
        r"\bhba1c\b",
        r"\bglycemic\s+control\b",
        r"\bcardiovascular\s+outcomes?\b",
        r"\bserum\s+creatinine\b",
        r"\bp-value\b",
        r"\bp\s*[<=]\s*0\.\d+\b",
        r"\b95%\s+ci\b",
        r"\bconfidence\s+interval\b",
        r"\bbiomarker\b"
    ]
    matched_metrics = [p for p in metric_patterns if re.search(p, text_lower)]

    mesh_patterns = [
        r"\bmesh\s+terms?\b",
        r"\bmedical\s+subject\s+headings?\b",
        r"\bpubmed\b"
    ]
    matched_mesh = [p for p in mesh_patterns if re.search(p, text_lower)]

    # 1. Fast Negative Rejection: Contains clear non-biomedical indicator and lacks clinical trial/drug design
    if matched_negatives and (len(matched_trial_design) == 0 and len(matched_drugs) == 0):
        return False, "Document rejected: Not a recognized biomedical or clinical trial paper. Please upload clinical research literature."

    # 2. Ollama zero-shot verification with llama3.1:8b
    try:
        prompt = f"""You are a strict biomedical literature validation classifier for a medical research platform.
Analyze the following text from the first 2 pages of an uploaded research document.
Determine whether it is a genuine biomedical, clinical trial, pharmacological, or healthcare research paper.

DOCUMENT EXCERPT (First 2 pages):
\"\"\"
{sample_text[:2000]}
\"\"\"

RULES:
- ACCEPT (BIOMEDICAL): Clinical trials, patient cohort studies, pharmacological research, drug interventions, physiological metrics, hazard ratios, or medical studies.
- REJECT (NON_BIOMEDICAL): Computer science, software projects, college project reports, synopses, syllabi, sports analytics, business, or non-medical papers.

Answer with exactly one word: BIOMEDICAL or NON_BIOMEDICAL.
Answer:"""
        r = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3.1:8b",
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": 10, "temperature": 0.0}
        }, timeout=25)
        if r.status_code == 200:
            resp = r.json().get("response", "").strip().upper()
            if "NON_BIOMEDICAL" in resp or "NON-BIOMEDICAL" in resp:
                return False, "Document rejected: Not a recognized biomedical or clinical trial paper. Please upload clinical research literature."
            if "BIOMEDICAL" in resp:
                return True, "Verified biomedical literature via Ollama Llama-3.1-8B classification."
    except Exception as e:
        print(f"Ollama note: {e}")

    # 3. Fallback rule engine if Ollama is unreachable
    if matched_negatives:
        return False, "Document rejected: Not a recognized biomedical or clinical trial paper. Please upload clinical research literature."

    clinical_score = (
        (2 if matched_trial_design else 0) +
        (2 if matched_mesh else 0) +
        (1 if matched_cohorts else 0) +
        (1 if matched_drugs else 0) +
        (1 if matched_metrics else 0)
    )

    if clinical_score >= 3:
        return True, "Verified biomedical literature via clinical trial markers."

    return False, "Document rejected: Not a recognized biomedical or clinical trial paper. Please upload clinical research literature."

test_samples = [
    ("College Project", "A Project Report on Deep Learning for Stock Market Prediction. Submitted by Rohit Sharma, Roll No 18BCE102. Bachelor of Technology in Computer Science. Department of CSE. Abstract: In this project report, we evaluate LSTM networks."),
    ("Sports Analytics", "IPL Cricket Player Performance Analytics using Machine Learning. Abstract: Sports analytics is vital for franchise decision making. We predict batting average and strike rate using Random Forest."),
    ("Course Syllabus", "Course Syllabus: CS401 Advanced Software Engineering. Semester VII. Web applications, frontend React.js, backend Node.js, and CI/CD pipelines. Marks distribution: Midterm 30%, Final 70%."),
    ("Clinical Trial", "Safety and efficacy of SGLT2 inhibitor dapagliflozin in patients with type 2 diabetes and chronic kidney disease: a double-blind, randomized, placebo-controlled trial. Methods: 400 hospitalized patients were randomized. Primary endpoint was eGFR decline (hazard ratio 0.61; 95% CI 0.51-0.72; p < 0.001). Adverse events were monitored.")
]

for label, text in test_samples:
    ok, reason = check_text_is_biomedical(text)
    status = "ACCEPTED" if ok else "REJECTED"
    print(f"[{status}] {label}: {reason}")
