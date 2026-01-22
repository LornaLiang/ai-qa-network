from pathlib import Path
import re
import mkdocs_gen_files

QA_DIR = Path("docs/qa")

EXCLUDE = {"SUMMARY.md", "_template.md", "index.md"}

# 允许：# 标题 或 #标题；允许前面有空白
H1_RE = re.compile(r"^\s*#(?!#)\s*(.+?)\s*$")

def read_h1_title(md_path: Path) -> str | None:
    lines = md_path.read_text(encoding="utf-8", errors="ignore").splitlines()

    in_fenced_code = False
    i = 0

    # 去掉可能的 UTF-8 BOM
    if lines:
        lines[0] = lines[0].lstrip("\ufeff")

    # 跳过 YAML front matter（MkDocs 支持的 meta 区块）
    if i < len(lines) and lines[i].strip() == "---":
        i += 1
        while i < len(lines):
            if lines[i].strip() == "---":
                i += 1
                break
            i += 1

    while i < len(lines):
        line = lines[i]
        s = line.strip()

        # 跳过 fenced code block
        if s.startswith("```") or s.startswith("~~~"):
            in_fenced_code = not in_fenced_code
            i += 1
            continue

        if not in_fenced_code:
            m = H1_RE.match(line)
            if m:
                return m.group(1)

        i += 1

    return None

def fallback_title_from_filename(p: Path) -> str:
    return p.stem

qa_files = []
if QA_DIR.exists():
    for p in QA_DIR.glob("*.md"):
        if p.name in EXCLUDE:
            continue
        qa_files.append(p)

# 排序：按读到的标题；读不到则按文件名
def sort_key(p: Path):
    return (read_h1_title(p) or fallback_title_from_filename(p)).lower()

qa_files.sort(key=sort_key)

lines = ["# Q&A\n"]
for p in qa_files:
    title = read_h1_title(p) or fallback_title_from_filename(p)
    lines.append(f"- [{title}]({p.name})")

with mkdocs_gen_files.open("qa/SUMMARY.md", "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
