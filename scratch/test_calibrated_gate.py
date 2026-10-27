import re
import requests
import pdfplumber
import os

def clean_and_extract_text(pdf_path):
    raw_pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for p in pdf.pages[:2]:
            t = p.extract_text()
            if t:
                raw_pages.append(t)
    full_raw = "\n".join(raw_pages)

    cleaned_lines = []
    for line in full_raw.splitlines():
        l_str = line.strip()
        l_lower = l_str.lower()
        if not l_str:
            continue
        # Strip metadata, copyright, author blocks
        if any(l_lower.startswith(prefix) for prefix in [
            "doi", "published", "editedby", "edited by", "reviewedby", "reviewed by",
            "correspondence", "*correspondence", "openaccess", "open access", "copyright",
            "all rights reserved", "received", "accepted", "citation", "orcid"
        ]):
            continue
        if "@" in l_str or re.search(r"^\d\s*(department|school|graduate|faculty|university|hospital|institute)", l_lower):
            continue
        if re.search(r"^(dr\.|prof\.|mr\.|ms\.)", l_lower):
            continue
        cleaned_lines.append(l_str)

    cleaned_text = "\n".join(cleaned_lines)
    words = cleaned_text.split()
    first_1500_words = " ".join(words[:1500])
    return first_1500_words

def check_biomedical_calibrated(pdf_path):
    extracted_text = clean_and_extract_text(pdf_path)
    if not extracted_text:
        return False, "Document is empty or contains no parseable text."

    text_lower = extracted_text.lower()

    # 1. Clear Non-Medical Rejection Patterns
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
        r"\bsoftware\s+manual\b",
        r"\buser\s+manual\b",
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
        r"\bcurriculum\s+vitae\b",
        r"\bresume\b",
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

    # 2. Broad Biomedical Indicators
    pharma_patterns = [
        r"\bpharmacology\b", r"\bpharmacokinetics\b", r"\bpharmacodynamics\b",
        r"\bdrug\b", r"\bmedication\b", r"\btherapy\b", r"\btherapeutic\b",
        r"\binhibitor\b", r"\bagonist\b", r"\bantagonist\b", r"\bdosage\b", r"\bdose\b",
        r"\bmonotherapy\b", r"\bcombination\s+therapy\b", r"\bmetabolic\s+modulator\b",
        r"\bsglt2\b", r"\bglp-?1\b", r"\binsulin\b", r"\bmetformin\b", r"\bantidiabetic\b",
        r"\bantimicrobial\b", r"\bantibiotic\b", r"\bchemotherapy\b", r"\btolerability\b",
        r"\badverse\s+events?\b", r"\badverse\s+reactions?\b", r"\bhypoglycemic\b"
    ]
    matched_pharma = [p for p in pharma_patterns if re.search(p, text_lower)]

    disease_patterns = [
        r"\bpathogenesis\b", r"\bpathophysiology\b", r"\betiology\b", r"\bmetabolic\b",
        r"\bglucose\s+metabolism\b", r"\bdiabetes\b", r"\bt2dm\b", r"\bt1dm\b",
        r"\bcardiovascular\b", r"\bcardiac\b", r"\bmyocardial\b", r"\bheart\s+failure\b",
        r"\bhfpef\b", r"\bkidney\b", r"\brenal\b", r"\bhepatic\b", r"\bliver\b",
        r"\binflammation\b", r"\binflammatory\b", r"\blipid\b", r"\bcholesterol\b",
        r"\binsulin\s+resistance\b", r"\bbeta-cell\b", r"\bmicrovascular\b",
        r"\bmacrovascular\b", r"\blesions\b", r"\bpathological\b", r"\bdysregulation\b",
        r"\bhypoxia\b", r"\bhypertension\b", r"\binfection\b", r"\boncology\b",
        r"\bcancer\b", r"\btumor\b", r"\bbiomarker\b"
    ]
    matched_disease = [p for p in disease_patterns if re.search(p, text_lower)]

    cohort_patterns = [
        r"\bpatients\b", r"\bsubjects\b", r"\bcohort\b", r"\bparticipants\b",
        r"\bclinical\b", r"\binpatient\b", r"\boutpatient\b", r"\bpopulation\b",
        r"\bsample\s+size\b", r"\binclusion\s+criteria\b", r"\bexclusion\s+criteria\b",
        r"\bendpoint\b", r"\bendpoints\b", r"\bglycemic\s+control\b", r"\bmortality\b",
        r"\bhospitalization\b", r"\bhba1c\b", r"\bbmi\b", r"\bejection\s+fraction\b",
        r"\bblood\s+pressure\b", r"\bsurvival\b", r"\bp-value\b", r"\bodds\s+ratio\b",
        r"\bhazard\s+ratio\b", r"\bconfidence\s+interval\b", r"\b95%\s+ci\b"
    ]
    matched_cohort = [p for p in cohort_patterns if re.search(p, text_lower)]

    journal_patterns = [
        r"\bfrontiers\b", r"\bpubmed\b", r"\belsevier\b", r"\blancet\b", r"\bjama\b",
        r"\bbmj\b", r"\bspringer\b", r"\bnature\s+medicine\b", r"\bnejm\b", r"\bplos\b",
        r"\bwiley\b", r"\boxford\b", r"\bbiomedical\b", r"\bendocrinology\b",
        r"\bcardiology\b", r"\boncology\b", r"\bpediatrics\b", r"\bmesh\b",
        r"\bclinicaltrials\.gov\b", r"\brandomized\s+controlled\s+trial\b",
        r"\bsystematic\s+review\b", r"\bmeta-analysis\b"
    ]
    matched_journal = [p for p in journal_patterns if re.search(p, text_lower)]

    # 3. Deterministic LLM verification via Ollama (llama3.1:8b)
    # Take first 400 words of scientific content for fast prompt evaluation
    words = extracted_text.split()
    llm_sample = " ".join(words[:400])

    prompt = f"""You are an expert biomedical and scientific document classifier.
Analyze the following document text:

\"\"\"
{llm_sample}
\"\"\"

TASK:
Determine if this document is biomedical literature.
Answer YES if the text discusses biomedical, healthcare, clinical, or pharmacological topics. Answer NO only if it is completely non-biomedical (e.g. computer science, sports, business, finance). Output strictly YES or NO.

Output strictly YES or NO.
Answer:"""

    llm_result = None
    try:
        r = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3.1:8b",
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": 5, "temperature": 0.0}
        }, timeout=25)
        if r.status_code == 200:
            resp = r.json().get("response", "").strip().upper()
            if "YES" in resp:
                llm_result = True
            elif "NO" in resp:
                llm_result = False
    except Exception as e:
        print(f"Ollama check note: {e}")

    # If LLM gave a definitive answer:
    if llm_result is True and not matched_negatives:
        return True, "Verified biomedical literature via Ollama Llama-3.1-8B (YES)."
    elif llm_result is False and (len(matched_pharma) == 0 and len(matched_disease) == 0):
        return False, "Document rejected: Not a recognized biomedical or clinical trial paper. Please upload clinical research literature."

    # 4. Calibrated Pattern Scoring
    if matched_negatives and (len(matched_pharma) == 0 and len(matched_disease) == 0):
        return False, "Document rejected: Not a recognized biomedical or clinical trial paper. Please upload clinical research literature."

    biomed_signals = (
        (1 if matched_pharma else 0) +
        (1 if matched_disease else 0) +
        (1 if matched_cohort else 0) +
        (1 if matched_journal else 0)
    )

    if biomed_signals >= 2:
        return True, f"Verified biomedical literature ({len(matched_pharma)} pharma, {len(matched_disease)} disease, {len(matched_cohort)} clinical markers)."

    return False, "Document rejected: Not a recognized biomedical or clinical trial paper. Please upload clinical research literature."

# Test on available PDFs
pdfs_to_test = [
    (r"C:\Projects\VeriNexa\backend\test_pdfs\SGLT2.pdf", "SGLT2 Review Paper"),
    (r"C:\Projects\VeriNexa\backend\test_pdfs\GLP1_SGLT2_2025.pdf", "GLP1 SGLT2 Trial Paper"),
    (r"C:\Projects\VeriNexa\data\medi.pdf", "Pediatric Antimicrobial Inpatient Paper")
]

for p, label in pdfs_to_test:
    if os.path.exists(p):
        ok, reason = check_biomedical_calibrated(p)
        print(f"[{'PASS' if ok else 'FAIL'}] {label} ({os.path.basename(p)}): {reason}")
    else:
        print(f"[SKIP] {label}: File not found at {p}")

print("\n--- Testing Non-Medical Documents ---")
non_med_tests = [
    ("College Report", "Final Year Project Report: Machine Learning Web Application in React.js. Submitted by Dept of Computer Science. Bachelor of Technology in CSE."),
    ("Cricket Analytics", "Sports Analytics in IPL Cricket: Predicting match outcomes and batsman batting average using random forest machine learning."),
    ("Software Manual", "Software User Manual: Installation Guide for Apache Kafka and Database Management System. CLI commands and configuration files."),
    ("Resume", "Curriculum Vitae: John Doe. Software Engineer with 5 years experience in Python, React, and AWS cloud infrastructure. Education: B.Tech in IT."),
    ("Corporate Budget", "Q3 Corporate Financial Budget: EBITDA increased by 14%. Consolidated balance sheet and stock market dividend payouts.")
]

for label, txt in non_med_tests:
    # Use the same logic on text
    text_lower = txt.lower()
    matched_neg = [p for p in non_biomed_indicators if re.search(p, text_lower)]
    matched_p = [p for p in pharma_patterns if re.search(p, text_lower)]
    matched_d = [p for p in disease_patterns if re.search(p, text_lower)]
    
    is_neg = matched_neg and (len(matched_p) == 0 and len(matched_d) == 0)
    print(f"[{'REJECTED' if is_neg else 'UNEXPECTED ACCEPT'}] {label}: {matched_neg[:2]}")
