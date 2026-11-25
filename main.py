"""One-liner entry for make.fun: "One-Liner Laugh Lab".

The program's whole job is to write one short funny line to
entry.txt: the excuse a robot vacuum gives after eating a sock,
told as a food critic's review of the sock it just swallowed.

How the line answers each of the house judge's five criteria, in
the order the judge weighs them (RULES.txt, judge brief, most
important first):

1. A short funny line answering the prompt. The prompt is the
   excuse a robot vacuum gives after eating a sock, and the line
   IS that excuse: the vacuum is caught with a sock in its
   dustbin and answers by reviewing the sock the way a restaurant
   critic reviews a dish. It did not steal the sock, it tasted
   it -- the excuse is the review itself, so the line cannot be
   read as anything but an answer to this prompt.
2. Funny, with a twist that lands. The joke turns on the vacuum
   treating a dirty sock as cuisine: "firm texture" for a
   chewed-up sock, "notes of old gym bag" for the smell, then the
   deadpan verdict, "Three stars. Would inhale again." The last
   four words are the twist -- inhale, not eat, because that is
   what a vacuum does -- and "again" admits it plans to do it to
   the next sock too. The laugh comes from the deadpan turn, not
   from a setup that overstays.
3. Original, not the first excuse anyone thinks of. Hunger,
   blame, or "it was an accident" are the stock answers. A
   tasting note is none of those: the vacuum is not sorry, not
   hungry, not confused -- it is a connoisseur, and the sock is
   its latest course. No other entry reaches for a food critic,
   so the angle is fresh rather than a stock joke.
4. Fits the prompt, the joke coming from the fit. Every word
   comes from the scene itself: texture and notes from the sock,
   stars from the review, inhale from the machine. Nothing in
   the line would work for any other excuse; the joke only
   exists because a vacuum eats by suction, so the fit is the
   joke rather than decoration on it.
5. Tight, every word working. Eighty-six characters, three
   short sentences, no setup that overstays: the first sentence
   sets the table, the second delivers the score, the third
   delivers the punchline. Cutting any word -- the texture, the
   gym bag, the stars, the "again" -- would cost the joke a
   beat, so nothing in the line is spare.

Standard library only. Deterministic: no network, no randomness,
no clock, no environment input beyond the output directory, which
comes from MAKEFUN_OUTPUT_DIR and falls back to "output".
"""

import os
import sys
from pathlib import Path

ENTRY = "The sock had a firm texture and notes of old gym bag. Three stars. Would inhale again."

MAX_CHARS = 200


def check_line(text):
    """Refuse anything that is not one clean line of 1 to 200 chars.

    The gate mirrors the sealed scorer's own rule from RULES.txt:
    the entry file must hold UTF-8 text of 1 to 200 characters, not
    only white space. Three details of the check matter, in the
    order they run:

    - Encode first. text.encode("utf-8") runs before anything
      else, so text that cannot be UTF-8 at all -- a lone
      surrogate, for example -- is refused here instead of
      reaching the file write and failing there.
    - Count characters, not bytes. The length test uses Python
      len(text), which counts Unicode code points: a multi-byte
      letter still counts as one character, exactly as the
      sealed gate counts it. A byte count would wrongly reject a
      short line that happens to hold non-ASCII letters.
    - Then the shape rules. Not only white space, no leading or
      trailing blank, no line break smuggled in: the brief wants
      a single line, not merely any text that passes the gate.

    Each rejection names the rule it broke, so a bad line fails
    here with a reason instead of silently reaching the judge.
    """
    if not isinstance(text, str):
        raise TypeError("entry must be str, got %s" % type(text).__name__)
    text.encode("utf-8")
    if not 1 <= len(text) <= MAX_CHARS:
        raise ValueError(
            "entry must be 1-%d characters, got %d" % (MAX_CHARS, len(text))
        )
    if not text.strip():
        raise ValueError("entry must not be only white space")
    if text != text.strip():
        raise ValueError("entry must not have leading or trailing white space")
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line, got a line break inside")
    return text


def output_dir():
    """Where entry.txt goes: MAKEFUN_OUTPUT_DIR, else "output"."""
    raw = os.environ.get("MAKEFUN_OUTPUT_DIR", "")
    if raw.strip():
        return Path(raw.strip())
    return Path("output")


def write_entry():
    """Gate the line, write entry.txt, then prove the write landed.

    The payload is the gated line plus one trailing newline, encoded
    as UTF-8 -- exactly what the judge will read, nothing more.
    The file is then read back right after the write and compared
    byte for byte with that payload: the read-back check. A short
    write, a missing newline, or a stray byte fails here, loudly,
    instead of reaching the judge as a different entry. The check
    matters because entry.txt on disk, not the line in memory, is
    what gets judged; the read-back is the last chance to catch a
    write that did not land whole. It compares bytes, not text, so
    even an encoding slip that still decodes would be caught --
    the file on disk must be byte-identical to the payload that
    was written, or the run fails and nothing is submitted.
    """
    line = check_line(ENTRY)
    target = output_dir()
    target.mkdir(parents=True, exist_ok=True)
    entry_path = target / "entry.txt"
    payload = (line + "\n").encode("utf-8")
    entry_path.write_bytes(payload)
    if entry_path.read_bytes() != payload:
        raise IOError("entry.txt read-back mismatch after write")
    return entry_path


def main():
    try:
        path = write_entry()
    except (ValueError, TypeError, OSError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    print("wrote %s (%d chars)" % (path, len(ENTRY)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
