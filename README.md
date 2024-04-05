# language-scripts

Scripts to help me with my Mandarin language study.

### upload_to_anki.py

Given that you have [Anki](https://apps.ankiweb.net/) installed and running on
your desktop, and the [AnkiConnect](https://ankiweb.net/shared/info/2055492159)
addon, this script feeds Mandarin words into your anki deck. 

Replace the `text_to_feed` and `deck_name` variables in the script, and run the
script.

```
python3 upload_to_anki.py
```

Currently, the script depends on words you care about being grouped together 
(i.e if you feed mandarin sentences, the script would try to search for meanings
for whole sentences, and can fail to find them in the dictionary). This works
out for me for the  time being because I usually note down interesting words in
a list, on Google Keep.

The expected format for `text_to_feed` might be something like:

```
text_to_feed = """
- 溫柔
- 下流
- 一趟
- 豪華
"""
```

Although, something like the following would also work:

```
text_to_feed = """
Lol: 溫柔
Lel: 下流
Lul: 一趟
Haha: 豪華
"""
```

(The above format is what you see when we copy from texting apps on a browser
sometimes.)
