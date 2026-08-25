import requests
from datetime import datetime

USERNAME = "aditi-0926"
README_FILE = "README.md"

START = "<!-- REPOSITORIES:START -->"
END = "<!-- REPOSITORIES:END -->"

RECENT_START = "<!-- RECENT:START -->"
RECENT_END = "<!-- RECENT:END -->"

# ---------------------------------------------------------

# GitHub

# ---------------------------------------------------------

response = requests.get(
f"https://api.github.com/users/{USERNAME}/repos",
params={
"per_page": 100,
"sort": "updated",
"direction": "desc"
},
headers={
"Accept": "application/vnd.github+json"
},
timeout=30
)

response.raise_for_status()

repos = response.json()

# ---------------------------------------------------------

# Ignore forks

# ---------------------------------------------------------

repos = [
repo for repo in repos
if not repo["fork"]
]

# ---------------------------------------------------------

# Sort by activity

# ---------------------------------------------------------

repos.sort(
key=lambda r: r["updated_at"],
reverse=True
)

# ---------------------------------------------------------

# Planet styles

# ---------------------------------------------------------

PLANETS = [
("🌌", "NEBULA"),
("🪐", "ORBIT"),
("🌙", "MOON"),
("🌍", "WORLD"),
("☄️", "COMET"),
("🔮", "CRYSTAL"),
("✨", "STAR"),
("🌒", "ECLIPSE"),
]

def format_date(date_string):

```
date = datetime.strptime(
    date_string,
    "%Y-%m-%dT%H:%M:%SZ"
)

return date.strftime("%d %b %Y")
```

def make_card(repo, index):

```
emoji, planet_type = PLANETS[index % len(PLANETS)]

name = repo["name"]

description = repo["description"]

if not description:
    description = "A little world still waiting to be explored."

language = repo["language"] or "unknown"

stars = repo["stargazers_count"]

forks = repo["forks_count"]

url = repo["html_url"]

updated = format_date(
    repo["updated_at"]
)

topics = repo.get("topics", [])

topic_html = ""

if topics:

    topic_html = "<br>".join(
        f"`{topic}`"
        for topic in topics[:4]
    )

return f"""
```

<td width="50%" valign="top">

<table width="100%" cellspacing="0" cellpadding="16">

<tr>

<td align="center">

<h1>{emoji}</h1>

<sub>✦ {planet_type} ✦</sub>

</td>

</tr>

<tr>

<td align="center">

<h2>
<a href="{url}">{name}</a>
</h2>

<p>

{description}

</p>

</td>

</tr>

<tr>

<td align="center">

<sub>

💻 {language}

   ✦   

⭐ {stars}

   ✦   

🍴 {forks}

</sub>

<br><br>

<sub>last signal · {updated}</sub>

</td>

</tr>

<tr>

<td align="center">

{topic_html}

</td>

</tr>

</table>

</td>
"""

# ---------------------------------------------------------

# Main repository galaxy

# ---------------------------------------------------------

cards = []

for i, repo in enumerate(repos):

```
cards.append(
    make_card(repo, i)
)
```

rows = []

for i in range(0, len(cards), 2):

```
row = "<tr>" + "".join(
    cards[i:i + 2]
) + "</tr>"

rows.append(row)
```

galaxy = f"""

<table width="100%" cellspacing="20">

{''.join(rows)}

</table>
"""

# ---------------------------------------------------------

# Recent signals

# ---------------------------------------------------------

recent = repos[:3]

recent_cards = []

for repo in recent:

```
name = repo["name"]

url = repo["html_url"]

updated = format_date(
    repo["updated_at"]
)

recent_cards.append(
    f"""
```

<tr>
<td align="center">

✦  

<a href="{url}"><b>{name}</b></a>

  ✦  

<sub>{updated}</sub>

</td>
</tr>
"""
    )

recent_section = f"""

<table width="100%" cellspacing="8">

{''.join(recent_cards)}

</table>
"""

# ---------------------------------------------------------

# Read README

# ---------------------------------------------------------

with open(
README_FILE,
"r",
encoding="utf-8"
) as f:

```
readme = f.read()
```

# ---------------------------------------------------------

# Replace repository section

# ---------------------------------------------------------

start = readme.find(START)

end = readme.find(END)

if start == -1 or end == -1:

```
raise RuntimeError(
    "Repository markers not found."
)
```

readme = (
readme[:start + len(START)]
+ "\n"
+ galaxy
+ "\n"
+ readme[end:]
)

# ---------------------------------------------------------

# Replace recent section

# ---------------------------------------------------------

start = readme.find(RECENT_START)

end = readme.find(RECENT_END)

if start == -1 or end == -1:

```
raise RuntimeError(
    "Recent markers not found."
)
```

readme = (
readme[:start + len(RECENT_START)]
+ "\n"
+ recent_section
+ "\n"
+ readme[end:]
)

# ---------------------------------------------------------

# Save

# ---------------------------------------------------------

with open(
README_FILE,
"w",
encoding="utf-8"
) as f:

```
f.write(readme)
```

print(
f"🌌 Galaxy updated with {len(repos)} repositories."
)
