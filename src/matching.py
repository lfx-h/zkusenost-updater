import pandas as pd
import re
from rapidfuzz import process, fuzz
from preprocessing import clean_text

# Precompile regular expressions for speed.
punctuation_re = re.compile(r"[,.]")
digit_re = re.compile(r'\d')

def generate_phrases(text: str, max_words=4):
    """
    Generate a set of n-grams (from 1 to max_words) from the given text.
    Punctuation is removed from words, and only words with at least 3 characters are used.
    """
    words = text.split()
    phrases = set()
    for n in range(1, max_words + 1):
        for i in range(len(words) - n + 1):
            # Remove commas and dots from each word.
            cleaned_words = [punctuation_re.sub("", word) for word in words[i:i+n]]
            if cleaned_words:
                phrase = " ".join(cleaned_words).lower()
                phrases.add(phrase)
    return phrases

def find_products_in_review(review: str, product_df: pd.DataFrame, threshold=0.88):
    """
    For a given review, find product names that have a fuzzy matching score
    above the threshold. The threshold here is given as a fraction (e.g. 0.88),
    but RapidFuzz uses an integer scale [0, 100], so we convert accordingly.
    """
    review = re.sub(r'([,.])(?=\S)', r'\1 ', review)
    review = clean_text(review)
    review = review.lower().strip()
    phrases = generate_phrases(review)
    single_word_blacklist = {"life", "gold", "multi", "", "relax"}
    
    candidate_default      = product_df["nazev_lower"].tolist()
    candidate_nostar       = product_df["nazev_lower_nostar"].tolist()
    candidate_nodigits     = product_df["nazev_lower_nodigits"].tolist()
    candidate_nodigits_ns  = product_df["nazev_lower_nodigits_nostar"].tolist()
    
    score_cutoff = threshold * 100

    results = []
    
    for phrase in phrases:
        has_digits = bool(digit_re.search(phrase))
        contains_star = "star" in phrase
        
        if not contains_star and phrase not in single_word_blacklist:
            candidate_list = candidate_nodigits_ns if not has_digits else candidate_nostar
        else:
            candidate_list = candidate_nodigits if not has_digits else candidate_default
        
        best = process.extractOne(
            phrase,
            candidate_list,
            scorer=fuzz.ratio,
            score_cutoff=score_cutoff
        )
        
        if best:
            match_str, score, idx = best
            row = product_df.iloc[idx]
            results.append({
                "ID": row["ID"],
                "nazev": row["nazev"],
                "phrase": phrase,
                "score": score / 100.0
            })
    
    result_df = pd.DataFrame(results, columns=["ID", "nazev", "phrase", "score"])
    
    if not result_df.empty:
        result_df = result_df.sort_values(by="score", ascending=False) \
                             .drop_duplicates(subset="nazev", keep="first")
    return result_df
