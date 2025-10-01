import pandas as pd
from langdetect import detect
from deep_translator import GoogleTranslator
import time
import sys
def load_language(file='test.csv'):
    # Load your CSV
    df = pd.read_csv(file, keep_default_na=False)

    # Clean up line breaks and whitespace
    df['comment'] = df['comment'].astype(str).str.replace('\n', ' ').str.strip()

    # Translation cache
    translation_cache = {}

    # Prepare output list
    translated_rows = []

    # Total number of rows
    total = len(df)
    # Loop through each row manually
    for i, row in enumerate(df.itertuples(index=False), start=1):
        text = row.comment
        try:
            lang = detect(text)
            if lang == 'en':
                translated_rows.append({'comment': text, 'rating_type': row.rating_type})
            else:
                if text in translation_cache:
                    translated = translation_cache[text]
                else:
                    translated = GoogleTranslator(source='auto', target='en').translate(text)
                    translation_cache[text] = translated
                time.sleep(0.1)
                translated_rows.append({'comment': translated, 'rating_type': row.rating_type})
        except Exception:
            pass  # Skip translation errors

        # Update progress
        progress = round((i / total) * 100, 2)
        sys.stdout.write(f"\rProgress: {progress}%")
        sys.stdout.flush()

    # Convert to DataFrame
    translated_df = pd.DataFrame(translated_rows)

    # Save to output file
    translated_df.to_csv(file, index=False)


