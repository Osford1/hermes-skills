# Pinyin for a Chinese string (tone marks). Usage:
#   python pinyin.py <chinese-text>
#   echo "中文" | python pinyin.py                        (reads stdin if first arg is '-'
#   python pinyin.py -f input.txt                      (one line per line of file)
import sys
from pypinyin import lazy_pinyin, Style

def annotate(s):
    return ' '.join(lazy_pinyin(s, style=Style.TONE))

if len(sys.argv) > 1 and sys.argv[1] == '-f':
    with open(sys.argv[2], encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.strip():
                print(line, '||', annotate(line))
else:
    text = ' '.join(sys.argv[1:])
    if not text:
        text = sys.stdin.read()
    for line in text.splitlines():
        if line.strip():
            print(line, '||', annotate(line))
