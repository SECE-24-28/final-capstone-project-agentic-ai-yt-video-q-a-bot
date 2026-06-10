import json
import re
from typing import List, Dict, Optional, Tuple


def parse_mcq(raw: str) -> List[Dict]:
    """
    Parse LLM output into list of MCQ dicts.
    Each dict: {question, options: {A,B,C,D}, answer}
    """
    # Strip markdown code fences if present
    text = re.sub(r"```(?:json)?", "", raw).strip()

    # Try direct parse first
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return _validate(data)
    except Exception:
        pass

    # Try extracting the first JSON array from the text
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            if isinstance(data, list):
                return _validate(data)
        except Exception:
            pass

    return []


def _validate(data: List[Dict]) -> List[Dict]:
    out = []
    for item in data:
        if not isinstance(item, dict):
            continue
        q = item.get("question", "").strip()
        opts = item.get("options", {})
        ans = str(item.get("answer", "")).strip().upper()
        if q and isinstance(opts, dict) and ans in ("A", "B", "C", "D"):
            # Ensure all 4 options exist
            if all(k in opts for k in ("A", "B", "C", "D")):
                out.append({"question": q, "options": opts, "answer": ans})
    return out


def grade_quiz(questions: List[Dict], user_answers: Dict[int, str]) -> Dict:
    """
    Grade quiz. user_answers = {0: "A", 1: "C", ...}
    Returns result dict.
    """
    total = len(questions)
    correct = 0
    review = []

    for i, q in enumerate(questions):
        user_ans = user_answers.get(i, "")
        correct_ans = q["answer"]
        is_correct = user_ans.upper() == correct_ans
        if is_correct:
            correct += 1
        review.append({
            "num": i + 1,
            "question": q["question"],
            "user_answer": user_ans,
            "correct_answer": correct_ans,
            "user_text": q["options"].get(user_ans, "—"),
            "correct_text": q["options"].get(correct_ans, ""),
            "is_correct": is_correct,
        })

    wrong = total - correct
    pct = round((correct / total) * 100) if total > 0 else 0
    grade = _grade(pct)

    return {
        "total": total,
        "correct": correct,
        "wrong": wrong,
        "percentage": pct,
        "grade": grade,
        "review": review,
    }


def _grade(pct: int) -> str:
    if pct >= 90: return "A+"
    if pct >= 80: return "A"
    if pct >= 70: return "B"
    if pct >= 60: return "C"
    if pct >= 50: return "D"
    return "F"


def export_txt(result: Dict, video_id: str) -> str:
    lines = [
        "YouTube Intelligence — Quiz Results",
        "=" * 40,
        f"Video ID  : {video_id}",
        f"Score     : {result['correct']}/{result['total']}",
        f"Percentage: {result['percentage']}%",
        f"Grade     : {result['grade']}",
        f"Correct   : {result['correct']}",
        f"Wrong     : {result['wrong']}",
        "",
        "Review",
        "-" * 40,
    ]
    for r in result["review"]:
        status = "CORRECT" if r["is_correct"] else "WRONG"
        lines += [
            f"Q{r['num']}: {r['question']}",
            f"  Your answer    : {r['user_answer']}. {r['user_text']}",
            f"  Correct answer : {r['correct_answer']}. {r['correct_text']}",
            f"  Result         : {status}",
            "",
        ]
    return "\n".join(lines)
