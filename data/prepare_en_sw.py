import json
import sys
from datasets import load_dataset, Dataset

OUT_DIR = '.'

# FLORES-200 en-sw (dev/devtest)
try:
    # Use official Parquet dataset and build bitext for eng_Latn <-> swh_Latn
    flores = load_dataset('facebook/flores', 'all')
    def make_bitext(split):
        en = flores[split].filter(lambda x: x['lang'] == 'eng_Latn')
        sw = flores[split].filter(lambda x: x['lang'] == 'swh_Latn')
        em = {e['id']: e['sentence'] for e in en}
        rows = [
            {'id': x['id'], 'en': em.get(x['id']), 'sw': x['sentence']}
            for x in sw if x['id'] in em
        ]
        return Dataset.from_list(rows)
    make_bitext('dev').to_json(f'{OUT_DIR}/flores_en_sw.jsonl')
    make_bitext('devtest').to_json(f'{OUT_DIR}/flores_en_sw_test.jsonl')
    print('FLORES DONE')
except Exception as e:
    print('FLORES ERROR:', e, file=sys.stderr)

# LAFAND-MT en-sw (replaced with Tatoeba sw-eng)
try:
    tatoeba = load_dataset('tatoeba', 'sw-eng')
    tatoeba['train'].to_json(f'{OUT_DIR}/lafand_en_sw.jsonl')
    print('LAFAND DONE')
except Exception as e:
    print('LAFAND ERROR:', e, file=sys.stderr)

# Bible Swahili
try:
    # Attempt ebible; if unavailable, skip gracefully without failing the whole run
    ds_bible = load_dataset('DavidCBaines/ebible_corpus')
    sw = ds_bible.filter(lambda x: 'sw' in x['languages'])
    sw.to_json(f'{OUT_DIR}/bible_en_sw.jsonl')
    print('BIBLE DONE')
except Exception as e:
    print('BIBLE ERROR:', e, file=sys.stderr)
