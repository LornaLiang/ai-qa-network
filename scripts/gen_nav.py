from pathlib import Path
import re
import mkdocs_gen_files

ROOT = Path("docs/qa")

CATEGORIES = [
    "01-math",
    "02-deep-learning",
    "03-transformer",
    "04-llm",
    "05-training-alignment",
    "06-inference",
    "07-rag",
    "08-multimodal",
    "09-evaluation",
    "10-safety-privacy",
]

CATEGORY_TITLES = {
    "01-math": "数学基础",
    "02-deep-learning": "深度学习",
    "03-transformer": "Transformer",
    "04-llm": "LLM",
    "05-training-alignment": "训练与对齐",
    "06-inference": "推理",
    "07-rag": "RAG",
    "08-multimodal": "多模态",
    "09-evaluation": "评估与基准",
    "10-safety-privacy": "安全与隐私",
}

EXCLUDE = {"SUMMARY.md", "_template.md"}  # index.md 由脚本生成
H1_RE = re.compile(r"^\s*#(?!#)\s*(.+?)\s*$")


def read_h1_title(md_path: Path) -> str | None:
    lines = md_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    if not lines:
        return None
    lines[0] = lines[0].lstrip("\ufeff")  # remove BOM

    i = 0
    in_code = False

    # skip YAML front matter
    if lines[i].strip() == "---":
        i += 1
        while i < len(lines):
            if lines[i].strip() == "---":
                i += 1
                break
            i += 1

    while i < len(lines):
        s = lines[i].strip()
        if s.startswith("```") or s.startswith("~~~"):
            in_code = not in_code
            i += 1
            continue
        if not in_code:
            m = H1_RE.match(lines[i])
            if m:
                return m.group(1).strip()
        i += 1
    return None


def label(cat: str) -> str:
    return CATEGORY_TITLES.get(cat, cat.replace("-", " ").title())


def list_articles(cat_dir: Path) -> list[Path]:
    files = []
    if not cat_dir.exists():
        return files
    for p in cat_dir.glob("*.md"):
        if p.name in EXCLUDE:
            continue
        if p.name.startswith("_"):
            continue
        if p.name.lower() == "index.md":
            continue
        files.append(p)
    files.sort(key=lambda x: (read_h1_title(x) or x.stem).lower())
    return files


# 1) generate category index pages
for cat in CATEGORIES:
    cat_dir = ROOT / cat
    cat_dir.mkdir(parents=True, exist_ok=True)  # ensure category exists even if empty

    articles = list_articles(cat_dir)

    lines = [
        f"# {label(cat)}",
        "",
        "## 本分类文章",
        "",
    ]
    if articles:
        for p in articles:
            title = read_h1_title(p) or p.stem
            lines.append(f"- [{title}]({p.name})")
    else:
        lines.append("_暂无文章。_")

    with mkdocs_gen_files.open(f"qa/{cat}/index.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# 2) generate SUMMARY for literate-nav
summary = ["# Q&A", ""]

for cat in CATEGORIES:
    summary.append(f"- [{label(cat)}]({cat}/index.md)")

    cat_dir = ROOT / cat
    for p in list_articles(cat_dir):
        title = read_h1_title(p) or p.stem
        summary.append(f"  - [{title}]({cat}/{p.name})")

    summary.append("")

with mkdocs_gen_files.open("qa/SUMMARY.md", "w", encoding="utf-8") as f:
    f.write("\n".join(summary).rstrip() + "\n")