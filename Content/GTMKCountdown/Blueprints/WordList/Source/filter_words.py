#!/usr/bin/env python3

import argparse
import sys
from contextlib import nullcontext
from pathlib import Path

from better_profanity import Profanity
from wordfreq import zipf_frequency


def read_words(paths: list[Path]) -> set[str]:
    words: set[str] = set()
    for path in paths:
        with path.open() as f:
            words.update(line.strip().lower() for line in f if line.strip())
    return words


def is_common_enough(word: str, min_zipf: float) -> bool:
    return zipf_frequency(word, "en") >= min_zipf


def is_mature(word: str, profanity: Profanity, mature_list: set[str], mature_allowlist: set[str]) -> bool:
    if word in mature_allowlist:
        return False
    return word in mature_list or profanity.contains_profanity(word)


def main() -> None:
    script_dir = Path(__file__).parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path, help="word list files, one word per line")
    parser.add_argument("-o", "--output", type=Path, default=None, help="output file (default: stdout)")
    parser.add_argument(
        "--min-zipf",
        type=float,
        default=2.5,
        help="minimum Zipf frequency to keep a word (0-8 scale, higher = more common; default: 2.5)",
    )
    parser.add_argument("--min-length", type=int, default=3, help="minimum word length to keep (default: 3)")
    parser.add_argument("--max-length", type=int, default=9, help="maximum word length to keep (default: none)")
    parser.add_argument(
        "--denylist",
        type=Path,
        default=script_dir / "denylist.txt",
        help=f"file of explicitly banned words, one per line (default: {script_dir / 'denylist.txt'})",
    )
    parser.add_argument(
        "--mature-list",
        type=Path,
        default=script_dir / "mature_list.txt",
        help="extra words to flag Mature beyond the automatic profanity check, one per line "
        f"(default: {script_dir / 'mature_list.txt'})",
    )
    parser.add_argument(
        "--mature-allowlist",
        type=Path,
        default=script_dir / "mature_allowlist.txt",
        help="words to never flag Mature, overriding the automatic profanity check, one per line "
        f"(default: {script_dir / 'mature_allowlist.txt'})",
    )
    args = parser.parse_args()

    words = read_words(args.inputs)
    total_in = len(words)

    denylist = read_words([args.denylist]) if args.denylist.exists() else set()
    mature_list = read_words([args.mature_list]) if args.mature_list.exists() else set()
    mature_allowlist = read_words([args.mature_allowlist]) if args.mature_allowlist.exists() else set()
    profanity = Profanity()

    kept = sorted(
        word
        for word in words
        if word not in denylist
        and len(word) >= args.min_length
        and (args.max_length is None or len(word) <= args.max_length)
        and is_common_enough(word, args.min_zipf)
    )

    mature_count = 0
    with (args.output.open("w") if args.output else nullcontext(sys.stdout)) as out:
        for word in kept:
            mature = is_mature(word, profanity, mature_list, mature_allowlist)
            mature_count += mature
            print(f"{word},{int(mature)}", file=out)

    print(
        f"{total_in} unique words in -> {len(kept)} kept "
        f"({total_in - len(kept)} dropped: too rare or wrong length), "
        f"{mature_count} flagged Mature",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
