from rapidfuzz import fuzz
from typing import List, Dict, Tuple
import unicodedata
import re

FUZZY_THRESHOLD = 80

def normalize(text: str) -> str:
    text = text.lower().strip()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    text = re.sub(r'\W+', ' ', text)
    return text.strip()

def match_strings(A: List[str], B: List[str]) -> Dict[str, Tuple[str, float]]:
    normalized_B = [(b, normalize(b)) for b in B]
    matches = {}

    def first_n_words(s: str, n: int) -> str:
        words = s.split()
        return " ".join(words[:n]) if len(words) >= n else ""

    for a in A:
        norm_a = normalize(a)
        best_match = None
        best_score = 0

        # Step 1: regular fuzzy matching
        for original_b, norm_b in normalized_B:
            score = fuzz.token_set_ratio(norm_a, norm_b)
            if score > best_score:
                best_score = score
                best_match = original_b

        # Step 2 and 3: second chance if below threshold
        if best_score < FUZZY_THRESHOLD:
            best_match2 = None
            best_score2 = 0

            # Step 2: containment check after removing spaces
            norm_a_nospace = norm_a.replace(" ", "")
            for original_b, norm_b in normalized_B:
                norm_b_nospace = norm_b.replace(" ", "")
                small, large = (norm_a_nospace, norm_b_nospace) if len(norm_a_nospace) < len(norm_b_nospace) else (norm_b_nospace, norm_a_nospace)
                if small.lower() in large.lower():
                    best_match2 = original_b
                    best_score2 = FUZZY_THRESHOLD
                    break

            # Step 3: fuzzy matching on first 2 words if both have >=2 words
            if best_match2 is None:
                a_first2 = first_n_words(norm_a, 2)
                if a_first2:
                    for original_b, norm_b in normalized_B:
                        b_first2 = first_n_words(norm_b, 2)
                        if b_first2:
                            score2 = fuzz.token_set_ratio(a_first2, b_first2)
                            if score2 > best_score2:
                                best_score2 = score2
                                best_match2 = original_b

            if best_score2 >= FUZZY_THRESHOLD:
                best_match = best_match2
                best_score = best_score2
            else:
                best_match = None
                best_score = best_score2

        matches[a] = (best_match, best_score)

    return matches

def unique_list(seq):
    seen = set()
    return [x for x in seq if not (x in seen or seen.add(x))]

def unique_sorted(strings: List[str]) -> List[str]:
    return sorted(set(strings), key=lambda s: s.lower())
