"""``python -m thunderbot.harness check [DIR]`` and ``python -m thunderbot.harness export DIR``."""

from __future__ import annotations

import sys

from . import HarnessError, current, export, load


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[0] == "export":
        print(f"Wrote the built-in harness to {export(argv[1])}. Edit it, then set TB_HARNESS_DIR to that path.")
        return 0
    if argv and argv[0] == "check":
        try:
            h = load(argv[1]) if len(argv) > 1 else current()
        except HarnessError as e:
            print("This harness would not be used:")
            for p in e.problems:
                print(f"  - {p}")
            return 1
        for p in h.problems:
            print(f"  not used: {p}")
        print(f"harness {h.id} ({h.source}{', ' + h.path if h.path else ''}); memory mode {h.memory_mode}")
        for name, role in h.roles.items():
            print(f"  {name}: may {role.may}; prompt {role.prompt_path} ({len(role.prompt)} characters)")
        return 1 if h.problems else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
