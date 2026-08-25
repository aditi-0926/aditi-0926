import requests
from datetime import datetime

USERNAME = "aditi-0926"
README_FILE = "README.md"

START = "<!-- REPOSITORIES:START -->"
END = "<!-- REPOSITORIES:END -->"

RECENT_START = "<!-- RECENT:START -->"
RECENT_END = "<!-- RECENT:END -->"

# ---------------------------------------------------------
# Fetch repositories from GitHub
# ---------------------------------------------------------

response = requests.get(
    f"https://api.github.com/users/{USERNAME}/repos",
    params={
        "per_page": 100,
        "sort": "updated",
        "direction": "desc",
    },
    headers={"Accept": "application/vnd.github+json"},
    timeout=30,
)
response.raise_for_status()
repos = response.json()

# Ignore forks
repos = [repo for repo in repos if not repo["fork"]]

# Sort by most recently updated
repos.sort(key=lambda r: r["updated_at"], reverse=True)

# ---------------------------------------------------------
# Planet styles — cycled per repo, with language-aware picks
# ---------------------------------------------------------

LANGUAGE_PLANETS = {
    "python": ("🪐", "ORBIT"),
    "jupyter notebook": ("🔮", "NEBULA"),
    "javascript": ("☄️", "COMET"),
    "typescript": ("☄️", "COMET"),
    "sql": ("🌍", "WORLD"),
    "html": ("🌙", "MOON"),
    "css": ("🌙", "MOON"),
}

DEFAULT_PLANETS = [
    ("🌌", "NEBULA"),
    ("🪐", "ORBIT"),
    ("🌙", "MOON"),
    ("🌍", "WORLD"),
    ("☄️", "COMET"),
    ("🔮", "CRYSTAL"),
    ("✨", "STAR"),
    ("🌒", "ECLIPSE"),
]


def pick_planet(repo, index):
    language = (repo["language"] or "").lower()
    topics = [t.lower() for t in repo.get("topics", [])]

    if "nlp" in topics or "sentiment" in repo["name"].lower():
        return ("🌙", "SIGNAL")
    if "machine-learning" in topics or "ml" in topics:
        return ("🔮", "NEBULA")
    if language in LANGUAGE_PLANETS:
        return LANGUAGE_PLANETS[language]
    return DEFAULT_PLANETS[index % len(DEFAULT_PLANETS)]


def format_date(date_string):
    date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
    return date.strftime("%d %b %Y")


def make_card(repo, index):
    emoji, planet_type = pick_planet(repo, index)
    name = repo["name"]
    description = repo["description"] or "A little world still waiting to be explored."
    language = repo["language"] or "unknown"
    stars = repo["stargazers_count"]
    forks = repo["forks_count"]
    url = repo["html_url"]
    updated = format_date(repo["updated_at"])
    topics = repo.get("topics", [])
    topic_html = "<br>".join(f"`{topic}`" for topic in topics[:4]) if topics else ""

    return f"""<td width="50%" valign="top">
<table width="100%" cellspacing="0" cellpadding="16">
<tr><td align="center">
<h1>{emoji}</h1>
<sub>✦ {planet_type} ✦</sub>
</td></tr>
<tr><td align="center">
<h2><a href="{url}">{name}</a></h2>
<p>{description}</p>
</td></tr>
<tr><td align="center">
<sub>💻 {language} &nbsp;✦&nbsp; ⭐ {stars} &nbsp;✦&nbsp; 🍴 {forks}</sub>
<br><br>
<sub>last signal · {updated}</sub>
</td></tr>
<tr><td align="center">
{topic_html}
</td></tr>
</table>
</td>"""


# ---------------------------------------------------------
# Build the main repository galaxy (2 planets per row)
# ---------------------------------------------------------

cards = [make_card(repo, i) for i, repo in enumerate(repos)]
rows = ["<tr>" + "".join(cards[i:i + 2]) + "</tr>" for i in range(0, len(cards), 2)]

if rows:
    galaxy = f'<table width="100%" cellspacing="20">\n{"".join(rows)}\n</table>'
else:
    galaxy = '<div align="center">🌙 no repositories found yet</div>'

# ---------------------------------------------------------
# Build the recent-signals section (last 3 updated repos)
# ---------------------------------------------------------

recent = repos[:3]
recent_cards = []
for repo in recent:
    name = repo["name"]
    url = repo["html_url"]
    updated = format_date(repo["updated_at"])
    recent_cards.append(
        f'<tr><td align="center">✦ &nbsp;<a href="{url}"><b>{name}</b></a>&nbsp; ✦ &nbsp;<sub>{updated}</sub></td></tr>'
    )

if recent_cards:
    recent_section = f'<table width="100%" cellspacing="8">\n{"".join(recent_cards)}\n</table>'
else:
    recent_section = '<div align="center">✦ no recent activity</div>'

# ---------------------------------------------------------
# Read the existing README
# ---------------------------------------------------------

with open(README_FILE, "r", encoding="utf-8") as f:
    readme = f.read()

# ---------------------------------------------------------
# Replace the repository-galaxy section between its markers
# ---------------------------------------------------------

start = readme.find(START)
end = readme.find(END)

if start == -1 or end == -1:
    raise RuntimeError("Repository markers not found.")

readme = (
    readme[: start + len(START)]
    + "\n\n"
    + galaxy
    + "\n\n"
    + readme[end:]
)

# ---------------------------------------------------------
# Replace the recent-signals section between its markers
# ---------------------------------------------------------

start = readme.find(RECENT_START)
end = readme.find(RECENT_END)

if start == -1 or end == -1:
    raise RuntimeError("Recent markers not found.")

readme = (
    readme[: start + len(RECENT_START)]
    + "\n\n"
    + recent_section
    + "\n\n"
    + readme[end:]
)

# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

with open(README_FILE, "w", encoding="utf-8") as f:
    f.write(readme)

print(f"🌌 Galaxy updated with {len(repos)} repositories.")
