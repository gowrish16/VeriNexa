from integrity_check import search_within_paper, query_ollama

def check_integrity_custom(fake_abstract, paper_id, topic_query):
    """
    Same logic as check_integrity, but lets us inject a fake abstract
    to deliberately test whether the system catches a real mismatch.
    """
    supporting_chunks = search_within_paper(paper_id, topic_query)
    supporting_text = "\n".join([text for _, text in supporting_chunks])

    prompt = f"""You are checking whether a research paper's abstract accurately reflects its own detailed results.

Important: In medical research, a "reduction" or "decrease" in a value (like body weight, HbA1c, or blood glucose) is often the DESIRED, POSITIVE outcome of a treatment, not a negative one. Do not treat a reported reduction as contradicting a claim of "improvement" unless the abstract explicitly claims an increase.

--- Abstract ---
{fake_abstract}

--- Detailed results text from the same paper (on the topic: {topic_query}) ---
{supporting_text}

Based only on the text above, answer in this exact format:
VERDICT: [CONSISTENT / INCONSISTENT / UNCLEAR]
REASON: [one or two sentences explaining why, citing specific numbers if mentioned]

Use INCONSISTENT only if the abstract makes a claim that is clearly not supported by, or actually contradicts, the detailed results shown — not merely because the wording differs.
"""
    result = query_ollama(prompt)
    return result


if __name__ == "__main__":
    fake_abstract = (
        "Background: We aimed to assess the safety and efficiency of SGLT2 inhibitors. "
        "Results: SGLT2 inhibitor treatment caused a significant increase in body weight "
        "compared to placebo, raising concerns about its use as an adjunct to insulin therapy."
    )

    paper_id = 1
    topic_query = "SGLT2 inhibitor effect on body weight"

    print("Testing with a DELIBERATELY WRONG abstract claim (weight GAIN instead of loss)\n")
    verdict = check_integrity_custom(fake_abstract, paper_id, topic_query)

    print("=== Integrity Check Verdict ===")
    print(verdict)