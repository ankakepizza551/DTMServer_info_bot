"""音楽理論まわりの共通ユーティリティ(複数Cogから参照)"""

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

_ALIASES = {
    "DB": "C#", "EB": "D#", "GB": "F#", "AB": "G#", "BB": "A#",
}


def parse_note(note: str) -> int | None:
    normalized = note.strip().upper().replace("♯", "#").replace("♭", "B")
    normalized = _ALIASES.get(normalized, normalized)
    try:
        return NOTE_NAMES.index(normalized)
    except ValueError:
        return None


# 各スケール度数の三和音の質(メジャー/マイナー/ディミニッシュ)
MAJOR_DEGREE_QUALITIES = ["", "m", "m", "", "", "m", "dim"]
NATURAL_MINOR_DEGREE_QUALITIES = ["m", "dim", "", "m", "m", "", ""]

MAJOR_SCALE_INTERVALS = [0, 2, 4, 5, 7, 9, 11]
NATURAL_MINOR_SCALE_INTERVALS = [0, 2, 3, 5, 7, 8, 10]
