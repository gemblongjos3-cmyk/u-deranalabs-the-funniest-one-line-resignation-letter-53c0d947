#!/usr/bin/env python3
"""Pick the best one-liner from a shortlist and write it to /output/entry.txt.

Contest: "The Funniest One-Line Resignation Letter" (make.fun, slug
u-deranalabs-the-funniest-one-line-resignation-letter-53c0d947, $10,
entries close 26 Nov 2026 23:15 WIB, at most 140 characters).

How the winner was chosen (staging scorecard, 26 Nov 2026):
- Rubric (/10 per dimension, total = 0.4*theme + 0.3*originality
  + 0.15*density + 0.15*format) over 10 candidates. Rubric ranking:
  #10 9.3 > #1 9.0 > #5 8.7 > #3 8.6 > #2 8.5.
- Model-combo panel (gemini-4-hydrogen, one call, status 200): top-3
  #10 9.5, #2 8.5, #4 8.0; panel winner #10.
- Decision: combined score = average of rubric and panel. Winner #10:
  (9.3 + 9.5) / 2 = 9.4 — #1 in the rubric AND #1 in the panel. The
  densest entry (two short sentences, no wasted word), the "on schedule"
  punchline flips the expectation of office projects that are always
  late, and the tone is exactly a one-line resignation: direct, no
  small talk.

Scoring honesty note: the panel published only its top-3, so #1, #5 and
#3 have no panel score on record and none is invented here. Their SCORES
entries below are UPPER BOUNDS — (rubric + 8.0) / 2, using the panel's
lowest published score (8.0) as the ceiling, since a finalist outside
the top-3 necessarily scored below it. The bound is conservative: even
at the bound, #1/#5/#3 stay below the winner's exact combined score
(9.4), so the pick does not depend on any invented number.

The program re-derives the pick from the scores: highest combined score
wins, ties go to the earliest candidate in the list.

v6 adds JUDGES_NOTES (the per-finalist judging notes from the scorecard)
and stricter validation: the entry must be exactly one line with no
leading/trailing whitespace, so a stray newline can never slip into the
submitted text.
"""

import os

WINNER = "I quit. My resignation is the only project here that's actually on schedule."
MAX_CHARS = 140
ONE_WORD = False

# Top 5 of 10 candidates by combined score, highest first.
FINALISTS = [
    "I quit. My resignation is the only project here that's actually on schedule.",
    "I quit — my plants have seen more daylight than I have this quarter.",
    "Dear boss, I'm resigning to pursue my lifelong dream of not being here.",
    "This letter serves as notice that my soul has already left the building.",
    "Effective immediately, I'm trading this job for a life.",
]

# Rubric totals (/10) from candidates.md, exactly as staged.
RUBRIC = {
    "I quit. My resignation is the only project here that's actually on schedule.": 9.3,
    "I quit — my plants have seen more daylight than I have this quarter.": 9.0,
    "This letter serves as notice that my soul has already left the building.": 8.7,
    "Effective immediately, I'm trading this job for a life.": 8.6,
    "Dear boss, I'm resigning to pursue my lifelong dream of not being here.": 8.5,
}

# Gemini panel scores (/10) from the scorecard; only the top-3 were
# published. #1, #5 and #3 have no panel score — see the docstring note.
PANEL = {
    "I quit. My resignation is the only project here that's actually on schedule.": 9.5,
    "Dear boss, I'm resigning to pursue my lifelong dream of not being here.": 8.5,
}

# Final combined score (/10) = (rubric + panel) / 2 where the panel
# score is published; otherwise an UPPER BOUND (rubric + 8.0) / 2 with
# 8.0 = the lowest published panel score. Winner's 9.4 is exact.
SCORES = {
    "I quit. My resignation is the only project here that's actually on schedule.": 9.4,
    "I quit — my plants have seen more daylight than I have this quarter.": 8.5,
    "Dear boss, I'm resigning to pursue my lifelong dream of not being here.": 8.5,
    "This letter serves as notice that my soul has already left the building.": 8.35,
    "Effective immediately, I'm trading this job for a life.": 8.3,
}

# Judging notes per finalist, quoted from the staging scorecard.
# The winner's note explains the unanimous pick; the other notes
# explain why each finalist fell short. Scores marked as bounds in
# SCORES stay bounds here — no panel score is invented.
JUDGES_NOTES = {
    "I quit. My resignation is the only project here that's actually on schedule.":
        "WINNER. Unanimous — #1 in the rubric (9.3) AND #1 in the panel "
        "(9.5), combined 9.4. Densest entry, 'on schedule' punchline "
        "flips the expectation of always-late office projects, tone is "
        "exactly a one-line resignation: direct, no small talk.",
    "I quit — my plants have seen more daylight than I have this quarter.":
        "Rubric #2 (9.0); outside the panel top-3. The daylight gag is "
        "vivid but the premise is a familiar work-from-home complaint.",
    "Dear boss, I'm resigning to pursue my lifelong dream of not being here.":
        "Panel #2 (8.5). Deadpan subversion of the sincere resignation "
        "cliche; the 'Dear boss' opener costs density.",
    "This letter serves as notice that my soul has already left the building.":
        "Good soul-left-the-building image (rubric 8.7); outside the "
        "panel top-3 and a touch wordier than the winner.",
    "Effective immediately, I'm trading this job for a life.":
        "Tightest line after the winner (rubric 8.6); outside the panel "
        "top-3, and 'trading this job for a life' is a known trope.",
}


def score(text: str) -> float:
    """Final combined score (/10) for a candidate."""
    return float(SCORES[text])


def pick_winner() -> str:
    """Highest score wins; ties go to the earliest candidate."""
    best = FINALISTS[0]
    best_score = score(best)
    for candidate in FINALISTS[1:]:
        candidate_score = score(candidate)
        if candidate_score > best_score:
            best, best_score = candidate, candidate_score
    return best


def validate(text: str) -> None:
    # Stricter than the contest minimum: the entry must be exactly one
    # line, with no leading/trailing whitespace and no line breaks, so
    # the file we write is exactly the staged winner text.
    if text != text.strip():
        raise ValueError("entry must not have leading or trailing whitespace")
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line")
    if not (1 <= len(text) <= MAX_CHARS):
        raise ValueError(f"entry must be 1-{MAX_CHARS} characters, got {len(text)}")
    if not text.strip():
        raise ValueError("entry must contain non-whitespace text")
    if ONE_WORD and len(text.split()) != 1:
        raise ValueError("entry must be exactly one word")


def main() -> None:
    winner = pick_winner()
    validate(winner)

    print(f"{'score':>6}  candidate")
    for candidate in sorted(FINALISTS, key=score, reverse=True):
        mark = "  <-- pick" if candidate == winner else ""
        print(f"{score(candidate):>6.2f}  {candidate}{mark}")
    print(f"judge: {JUDGES_NOTES[winner]}")

    os.makedirs("/output", exist_ok=True)
    with open("/output/entry.txt", "w", encoding="utf-8", newline="") as f:
        f.write(winner)


if __name__ == "__main__":
    main()
