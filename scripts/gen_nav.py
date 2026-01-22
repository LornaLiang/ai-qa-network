from pathlib import Path
import mkdocs_gen_files

QA_DIR = Path("docs/qa")

EXCLUDE = {
    "SUMMARY.md",
    "_template.md",
    "index.md",
}

def title_from_filename(p: Path) -> str:
    # 文件名转标题：math-test -> Math Test
    stem = p.stem.replace("_", "-")
    return " ".join([w.capitalize() for w in stem.split("-") if w])

qa_files = []
if QA_DIR.exists():
    for p in QA_DIR.glob("*.md"):
        if p.name in EXCLUDE:
            continue
        qa_files.append(p)

# 排序：按文件名（可改成按标题/日期）
qa_files.sort(key=lambda x: x.name.lower())

lines = ["# Q&A\n"]
for p in qa_files:
    title = title_from_filename(p)
    # SUMMARY.md 在 docs/qa 下，链接写当前目录相对路径
    lines.append(f"- [{title}]({p.name})")

content = "\n".join(lines) + "\n"

# 生成到 docs/qa/SUMMARY.md（虚拟写入，构建时产生）
with mkdocs_gen_files.open("qa/SUMMARY.md", "w", encoding="utf-8") as f:
    f.write(content)
