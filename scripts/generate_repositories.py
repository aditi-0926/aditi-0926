import os
import random
import re
import textwrap
from datetime import datetime

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont

USERNAME = "aditi-0926"
README_FILE = "README.md"
CARDS_DIR = "cards"

START = "<!-- REPOSITORIES:START -->"
END = "<!-- REPOSITORIES:END -->"

RECENT_START = "<!-- RECENT:START -->"
RECENT_END = "<!-- RECENT:END -->"

# ---------------------------------------------------------
# Fetch repositories from GitHub
# ---------------------------------------------------------

response = requests.get(
    f"https://api.github.com/users/{USERNAME}/repos",
    params={"per_page": 100, "sort": "updated", "direction": "desc"},
    headers={"Accept": "application/vnd.github+json"},
    timeout=30,
)
response.raise_for_status()
repos = response.json()

repos = [repo for repo in repos if not repo["fork"]]
repos.sort(key=lambda r: r["updated_at"], reverse=True)

# ---------------------------------------------------------
# Planet / tag styles — language-aware, cycled as a fallback
# ---------------------------------------------------------

LANGUAGE_TAGS = {
    "python": "ORBIT",
    "jupyter notebook": "NEBULA",
    "javascript": "COMET",
    "typescript": "COMET",
    "sql": "WORLD",
    "html": "MOON",
    "css": "MOON",
}

DEFAULT_TAGS = ["NEBULA", "ORBIT", "MOON", "WORLD", "COMET", "CRYSTAL", "STAR", "ECLIPSE"]

FALLBACK_DESCRIPTIONS = [
    "No description yet — still taking shape.",
    "A quiet corner of the galaxy, description pending.",
    "Work in progress — the story hasn't been written yet.",
    "Early days for this one. More soon.",
    "This world hasn't been mapped yet.",
]


def pick_tag(repo, index):
    language = (repo["language"] or "").lower()
    topics = [t.lower() for t in repo.get("topics", [])]
    if "nlp" in topics or "sentiment" in repo["name"].lower():
        return "SIGNAL"
    if "machine-learning" in topics or "ml" in topics:
        return "NEBULA"
    if language in LANGUAGE_TAGS:
        return LANGUAGE_TAGS[language]
    return DEFAULT_TAGS[index % len(DEFAULT_TAGS)]


def format_date(date_string):
    date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
    return date.strftime("%d %b %Y")


def safe_filename(name):
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", name).strip("-").lower()


# ---------------------------------------------------------
# Card image renderer — blurred nebula background behind a
# translucent panel, baked directly into the pixels so it
# renders identically everywhere (GitHub strips CSS blur/
# opacity from README HTML, so this can't be done with markup).
# ---------------------------------------------------------

W, H = 1600, 300

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
FONT_TITLE = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 46)
FONT_TAG = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 22)
FONT_DESC = ImageFont.truetype(FONT_DIR + "DejaVuSans.ttf", 30)
FONT_META = ImageFont.truetype(FONT_DIR + "DejaVuSans.ttf", 26)


def render_card(name, tag, description, meta, seed):
    rng = random.Random(seed)

    bg = Image.new("RGB", (W, H))
    top, bottom = (14, 8, 28), (52, 28, 84)
    px = bg.load()
    for y in range(H):
        t = y / H
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        for x in range(0, W, 4):  # coarse fill, blur smooths it — keeps render fast
            px[x, y] = (r, g, b)
    bg = bg.resize((W, H))

    star_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(star_layer)
    for _ in range(140):
        x, y = rng.randint(0, W), rng.randint(0, H)
        r = rng.choice([1, 1, 1, 2])
        sd.ellipse([x, y, x + r, y + r], fill=(230, 220, 255, rng.randint(60, 180)))
    bg = Image.alpha_composite(bg.convert("RGBA"), star_layer)
    blurred = bg.filter(ImageFilter.GaussianBlur(7))

    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    m = 10
    pd.rounded_rectangle(
        [m, m, W - m, H - m], radius=36,
        fill=(70, 48, 120, 105), outline=(228, 217, 255, 90), width=2,
    )
    card = Image.alpha_composite(blurred, panel)

    draw = ImageDraw.Draw(card)
    pad_x = 56
    draw.text((pad_x, 40), name, font=FONT_TITLE, fill=(240, 233, 255, 255))
    draw.text((pad_x, 100), f"✦ {tag} ✦", font=FONT_TAG, fill=(196, 168, 235, 255))
    wrapped = textwrap.fill(description, width=72)
    draw.multiline_text((pad_x, 150), wrapped, font=FONT_DESC, fill=(210, 199, 235, 255), spacing=8)
    draw.text((pad_x, H - 60), meta, font=FONT_META, fill=(170, 150, 210, 255))

    return card.convert("RGB")


# ---------------------------------------------------------
# Build one card image per repo, stacked vertically in the README
# ---------------------------------------------------------

os.makedirs(CARDS_DIR, exist_ok=True)

keep_files = set()
image_tags = []

for i, repo in enumerate(repos):
    tag = pick_tag(repo, i)
    description = repo["description"] or FALLBACK_DESCRIPTIONS[i % len(FALLBACK_DESCRIPTIONS)]
    language = repo["language"] or "unknown"
    meta = f"{language}  ·  ★ {repo['stargazers_count']}  ⋔ {repo['forks_count']}  ·  updated {format_date(repo['updated_at'])}"

    card = render_card(repo["name"], tag, description, meta, seed=i)
    filename = f"{safe_filename(repo['name'])}.png"
    card.save(os.path.join(CARDS_DIR, filename))
    keep_files.add(filename)

    image_tags.append(
        f'<a href="{repo["html_url"]}"><img src="{CARDS_DIR}/{filename}" width="800"></a>'
    )

# remove card images for repos that no longer exist / were renamed
for existing in os.listdir(CARDS_DIR):
    if existing not in keep_files:
        os.remove(os.path.join(CARDS_DIR, existing))

if image_tags:
    galaxy = '<div align="center">\n\n' + "\n\n<br>\n\n".join(image_tags) + "\n\n</div>"
else:
    galaxy = '<div align="center">🌙 no repositories found yet</div>'

# ---------------------------------------------------------
# Recent-signals section (last 3 updated repos, plain text list)
# ---------------------------------------------------------

recent_lines = []
for repo in repos[:3]:
    updated = format_date(repo["updated_at"])
    recent_lines.append(f'✦ &nbsp;<a href="{repo["html_url"]}"><b>{repo["name"]}</b></a>&nbsp; · <sub>{updated}</sub>')

if recent_lines:
    recent_section = '<div align="center">\n\n' + "<br>\n".join(recent_lines) + "\n\n</div>"
else:
    recent_section = '<div align="center">✦ no recent activity</div>'

# ---------------------------------------------------------
# Splice both sections into the README between their markers
# ---------------------------------------------------------

with open(README_FILE, "r", encoding="utf-8") as f:
    readme = f.read()


def splice(text, start_marker, end_marker, content):
    start = text.find(start_marker)
    end = text.find(end_marker)
    if start == -1 or end == -1:
        raise RuntimeError(f"Markers not found: {start_marker} / {end_marker}")
    return text[: start + len(start_marker)] + "\n\n" + content + "\n\n" + text[end:]


readme = splice(readme, START, END, galaxy)
readme = splice(readme, RECENT_START, RECENT_END, recent_section)

with open(README_FILE, "w", encoding="utf-8") as f:
    f.write(readme)

print(f"🌌 Galaxy updated with {len(repos)} repositories.")
