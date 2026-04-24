import os
import re
from collections import defaultdict

EXTENSIONS = (".webp",)

# capture base + number
pattern = re.compile(r"^(.*)_(\d+)$")


def parse(filename):
    name, ext = os.path.splitext(filename)
    match = pattern.match(name)

    if match:
        return match.group(1), int(match.group(2)), True

    return name, None, False


def main():
    folder = os.getcwd()

    files = [f for f in os.listdir(folder) if f.lower().endswith(EXTENSIONS)]

    groups = defaultdict(list)

    # group files by base name
    for f in files:
        base, num, ok = parse(f)
        groups[base].append((f, num, ok))

    deleted = 0
    renamed = 0

    for base, group in groups.items():

        versions = [g for g in group if g[2]]  # only _number files
        normal = [g for g in group if not g[2]]  # like aiming.webp

        # skip if no version system
        if not versions:
            continue

        # find latest version
        versions.sort(key=lambda x: x[1], reverse=True)
        keep_file = versions[0][0]

        target_final = f"{base}.webp"

        src_path = os.path.join(folder, keep_file)
        dst_path = os.path.join(folder, target_final)

        print(f"\nKEEP SOURCE: {keep_file}")
        print(f"FINAL NAME: {target_final}")

        # delete old versions
        for f, _, _ in versions[1:]:
            try:
                os.remove(os.path.join(folder, f))
                deleted += 1
                print(f"DELETE: {f}")
            except Exception as e:
                print(f"ERROR DELETE {f}: {e}")

        # delete existing clean file if exists
        if os.path.exists(dst_path):
            try:
                os.remove(dst_path)
                print(f"DELETE EXISTING FINAL: {target_final}")
            except Exception as e:
                print(f"ERROR DELETE FINAL: {e}")

        # rename best version → final name
        try:
            os.rename(src_path, dst_path)
            renamed += 1
            print(f"RENAME: {keep_file} -> {target_final}")
        except Exception as e:
            print(f"ERROR RENAME: {e}")

    print("\n====================")
    print(f"Renamed: {renamed}")
    print(f"Deleted: {deleted}")
    print("Done")


if __name__ == "__main__":
    main()