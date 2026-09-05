# data

`words.txt`: 62 700 lowercase words of 4+ letters. Derived from SCOWL (Spell Checker Oriented Word Lists) by Kevin Atkinson, British English, size 50, as packaged in Debian/Ubuntu `wbritish` 2020.12.07-2. Filter applied: `^[a-z]{4,}$`, sorted, unique. Regenerate with `tools/build_dict.sh`.

`exclude.txt`: one word per line, removed at load time. Empty by default.

SCOWL licence (MIT style):

> Copyright 2000-2019 by Kevin Atkinson. Permission to use, copy, modify, distribute and sell these word lists, the associated scripts, the output created from the scripts, and its documentation for any purpose is hereby granted without fee, provided that the above copyright notice appears in all copies and that both that copyright notice and this permission notice appear in supporting documentation. Kevin Atkinson makes no representations about the suitability of this array for any purpose. It is provided "as is" without express or implied warranty.

Full notice: http://wordlist.aspell.net/scowl-readme/

Swapping dictionaries later: replace `words.txt` with any file of one lowercase word per line (a licensed Oxford Languages word list, for example). Nothing else changes.
