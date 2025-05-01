import re
from fuzzywuzzy import process 

def is_likely_title_case(line):
    """Checks if a line looks like Title Case (heuristic)."""
    words = line.split()
    if not words:
        return False

    small_words = {'a', 'an', 'the', 'in', 'on', 'at', 'of', 'for', 'to', 'and', 'or', 'but', 'by', 'with', 'is', 'are', 'was', 'were', 'as', 'if', 'nor', 'so', 'yet'}
    tagline_starts = ['the', 'a', 'an', 'discover', 'experience', 'from', 'based', 'award-winning', 'new york times', 'bestseller', 'sequel', 'prequel', 'now', 'featuring', 'includes', 'with', 'stories', 'lessons']

    capitalized_count = 0
    significant_words = 0

    first_word_lower = words[0].lower().strip('\'".,!?;:()[]{}')
    if first_word_lower in tagline_starts and len(words) > 3:
        lower_count = sum(1 for w in words[1:] if w.islower() or not w.strip('\'".,!?;:()[]{}'))
        if lower_count / (len(words) -1) > 0.5:
            return False

    for i, word in enumerate(words):
        cleaned_word = word.strip('\'".,!?;:()[]{}')
        if not cleaned_word or not cleaned_word[0].isalpha():
            continue

        significant_words += 1
        is_first_word = (i == 0)
        is_last_word = (i == len(words) - 1) 

        if cleaned_word[0].isupper():
            if is_first_word or cleaned_word.lower() not in small_words:
                capitalized_count += 1
        elif not is_first_word and cleaned_word.lower() in small_words:
             pass 
        elif cleaned_word.isupper() and len(cleaned_word) > 1:
             capitalized_count += 1 
        elif '-' in cleaned_word and cleaned_word.split('-')[0][0].isupper():
             capitalized_count += 0.8 

    return significant_words > 0 and (capitalized_count / significant_words) >= 0.5 and len(line) < 70 


def is_likely_all_caps(line):
    """Checks if a line is predominantly uppercase letters and not too short/long."""
    if len(line) < 3 or len(line) > 60:
        return False
    letters_only = ''.join(filter(str.isalpha, line))
    if not letters_only:
        return False
    upper_count = sum(1 for char in letters_only if char.isupper())
    return (upper_count / len(letters_only)) > 0.85

def filter_extracted_text(text):
    """
    Filters OCR output to determine the most likely book title.
    Focuses on identifying a single, clean title line while ignoring irrelevant lines.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return ""

    MIN_TITLE_LENGTH = 3
    MAX_TITLE_LENGTH = 60

    irrelevant_keywords = {
        'edition', 'volume', 'chapter', 'bestseller', 'introduction', 'complete',
        'author', 'published', 'isbn', 'guide', 'answers', 'problems', 'stories',
        'novel', 'memoir', 'affair', 'life', 'secret', 'story', 'lessons',
        'techniques', 'strategies', 'principles', 'insights', 'how to', 'step-by-step',
        'collection', 'illustrated', 'annotated', 'selected', 'international',
        'national', 'number', 'one', 'york', 'times', 'renuka', 'gavrani', 'loneliness',
        'cage', 'solitude', 'home', 'was', 'my', 'is'
    }

    def is_likely_title(line):
        if len(line) < MIN_TITLE_LENGTH or len(line) > MAX_TITLE_LENGTH:
            return False
        if any(keyword in line.lower() for keyword in irrelevant_keywords):
            return False
        if is_likely_all_caps(line) or is_likely_title_case(line):
            return True
        return False

    potential_titles = [line for line in lines if is_likely_title(line)]

    if not potential_titles:
        return lines[0] if lines else ""

    return potential_titles[0]

def match_correct_title(ocr_filtered_query, search_results):
    """Given an OCR-based query and the API's search results,
       pick the closest official title from the API data."""
    if not search_results:
        return None, 0
    candidate_titles = [item.get("title","") for item in search_results if item.get("title")]
    if not candidate_titles:
         return None, 0


    best_match, best_score = process.extractOne(ocr_filtered_query, candidate_titles) 

    MATCH_THRESHOLD = 65 
    if best_score < MATCH_THRESHOLD:
        print(f"No close match found (Best: '{best_match}' with score {best_score} < {MATCH_THRESHOLD})")
        return None, best_score
    print(f"Found close match: '{best_match}' with score {best_score}")
    return best_match, best_score