import pandas as pd

def load_fasttext_format(path):
    texts= []
    labels= []
    with open(path, 'r', encoding = 'utf-8') as f:
        for line in f:
            parts = line.strip().split(' ',1)
            if len(parts) == 2:
                label, text = parts
                labels.append(label.replace('__label__',''))
                texts.append(text)
    return pd.DataFrame({'label': labels, 'text': texts})

df_train = load_fasttext_format('data/train.txt')
df_test = load_fasttext_format('data/test.txt')

print(df_train.head())