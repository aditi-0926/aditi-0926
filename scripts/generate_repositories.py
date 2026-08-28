import os
import re
import html
import requests
from datetime import datetime


USERNAME = "aditi-0926"

README_FILE = "README.md"
REPO_DIR = "assets/repos"

RECENT_START = "<!-- RECENT:START -->"
RECENT_END = "<!-- RECENT:END -->"


# ============================================================
# GITHUB API
# ============================================================

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

repositories = response.json()


# ============================================================
# REMOVE FORKS
# ============================================================

repositories = [
    repo
    for repo in repositories
    if not repo["fork"]
]


repositories.sort(
    key=lambda repo: repo["updated_at"],
    reverse=True
)


# ============================================================
# CREATE FOLDERS
# ============================================================

os.makedirs(
    REPO_DIR,
    exist_ok=True
)


# ============================================================
# HELPERS
# ============================================================

def esc(value):

    return html.escape(
        str(value),
        quote=True
    )


def slugify(name):

    return re.sub(
        r"[^a-zA-Z0-9_-]",
        "-",
        name
    )


def shorten(text, limit=110):

    if not text:

        return "A little universe still waiting to be explored."

    text = text.strip()

    if len(text) <= limit:

        return text

    return text[:limit - 3] + "..."


def time_ago(date_string):

    date = datetime.strptime(
        date_string,
        "%Y-%m-%dT%H:%M:%SZ"
    )

    now = datetime.utcnow()

    seconds = int(
        (now - date).total_seconds()
    )

    if seconds < 3600:

        return "just now"

    if seconds < 86400:

        hours = seconds // 3600

        return f"{hours}h ago"

    days = seconds // 86400

    if days == 1:

        return "1 day ago"

    if days < 7:

        return f"{days} days ago"

    weeks = days // 7

    if weeks == 1:

        return "1 week ago"

    if weeks < 5:

        return f"{weeks} weeks ago"

    months = days // 30

    if months == 1:

        return "1 month ago"

    return f"{months} months ago"


# ============================================================
# CARD COLOR THEMES
# ============================================================

THEMES = [

    {
        "a": "#6D5DFB",
        "b": "#B56CFF",
        "c": "#FF8FD8",
        "planet1": "#79A7FF",
        "planet2": "#A78BFA",
        "ring": "#E9D5FF"
    },

    {
        "a": "#4F8CFF",
        "b": "#8B7CFF",
        "c": "#C084FC",
        "planet1": "#60A5FA",
        "planet2": "#C084FC",
        "ring": "#DDD6FE"
    },

    {
        "a": "#8B5CF6",
        "b": "#D946EF",
        "c": "#FB7185",
        "planet1": "#C084FC",
        "planet2": "#F0ABFC",
        "ring": "#F5D0FE"
    },

    {
        "a": "#38BDF8",
        "b": "#818CF8",
        "c": "#C084FC",
        "planet1": "#67E8F9",
        "planet2": "#818CF8",
        "ring": "#C4B5FD"
    },

    {
        "a": "#6366F1",
        "b": "#A855F7",
        "c": "#EC4899",
        "planet1": "#818CF8",
        "planet2": "#F472B6",
        "ring": "#FBCFE8"
    }
]


# ============================================================
# PLANET
# ============================================================

def create_planet(theme, index):

    return f"""

    <defs>

        <radialGradient id="planet{index}">

            <stop
                offset="0%"
                stop-color="#FFFFFF"
                stop-opacity="0.95"
            />

            <stop
                offset="20%"
                stop-color="{theme['planet1']}"
            />

            <stop
                offset="100%"
                stop-color="{theme['planet2']}"
            />

        </radialGradient>

        <filter
            id="planetGlow{index}"
            x="-100%"
            y="-100%"
            width="300%"
            height="300%"
        >

            <feGaussianBlur
                stdDeviation="10"
                result="blur"
            />

            <feMerge>

                <feMergeNode in="blur"/>

                <feMergeNode in="SourceGraphic"/>

            </feMerge>

        </filter>

    </defs>


    <!-- planet glow -->

    <circle
        cx="125"
        cy="125"
        r="73"
        fill="{theme['planet2']}"
        opacity="0.20"
        filter="url(#planetGlow{index})"
    />


    <!-- orbit ring -->

    <ellipse
        cx="125"
        cy="125"
        rx="90"
        ry="28"
        fill="none"
        stroke="{theme['ring']}"
        stroke-width="3"
        opacity="0.65"
        transform="rotate(-18 125 125)"
    />


    <!-- planet -->

    <circle
        cx="125"
        cy="125"
        r="58"
        fill="url(#planet{index})"
    />


    <!-- planet shine -->

    <ellipse
        cx="107"
        cy="106"
        rx="22"
        ry="14"
        fill="#FFFFFF"
        opacity="0.15"
        transform="rotate(-30 107 106)"
    />


    <!-- little moon -->

    <circle
        cx="192"
        cy="95"
        r="7"
        fill="#FFFFFF"
        opacity="0.75"
    />

    """


# ============================================================
# STAR FIELD
# ============================================================

def create_stars():

    stars = []

    positions = [

        (410, 45),
        (520, 90),
        (680, 35),
        (790, 75),
        (930, 45),
        (1040, 105),
        (360, 165),
        (600, 180),
        (850, 150),
        (1010, 190),
        (460, 115),
        (730, 125)
    ]

    for i, (x, y) in enumerate(positions):

        duration = 2 + (i % 4)

        stars.append(
            f"""
            <circle
                cx="{x}"
                cy="{y}"
                r="{1.5 + (i % 3) * 0.7}"
                fill="#FFFFFF"
                opacity="0.35"
            >

                <animate
                    attributeName="opacity"
                    values="0.2;1;0.2"
                    dur="{duration}s"
                    repeatCount="indefinite"
                />

            </circle>
            """
        )

    return "\n".join(stars)


# ============================================================
# CREATE REPOSITORY CARD
# ============================================================

def create_card(repo, index):

    theme = THEMES[
        index % len(THEMES)
    ]

    name = repo["name"]

    description = shorten(
        repo["description"]
    )

    language = (
        repo["language"]
        or "Code"
    )

    stars = repo[
        "stargazers_count"
    ]

    forks = repo[
        "forks_count"
    ]

    topics = repo.get(
        "topics",
        []
    )[:4]

    updated = time_ago(
        repo["updated_at"]
    )


    topic_svg = ""

    topic_x = 320

    for topic in topics:

        width = max(
            75,
            len(topic) * 7.5 + 28
        )

        topic_svg += f"""

        <rect
            x="{topic_x}"
            y="184"
            width="{width}"
            height="26"
            rx="13"
            fill="{theme['b']}"
            opacity="0.28"
        />

        <text
            x="{topic_x + width / 2}"
            y="201"
            text-anchor="middle"
            font-family="Arial"
            font-size="11"
            fill="#F6F0FF"
        >
            {esc(topic)}
        </text>

        """

        topic_x += width + 9


    card = f"""
<svg
xmlns="http://www.w3.org/2000/svg"
width="1100"
height="250"
viewBox="0 0 1100 250"
>

<defs>

    <!-- colourful glass gradient -->

    <linearGradient
        id="glass"
        x1="0"
        y1="0"
        x2="1"
        y2="1"
    >

        <stop
            offset="0%"
            stop-color="{theme['a']}"
            stop-opacity="0.27"
        />

        <stop
            offset="45%"
            stop-color="#FFFFFF"
            stop-opacity="0.09"
        />

        <stop
            offset="100%"
            stop-color="{theme['c']}"
            stop-opacity="0.20"
        />

    </linearGradient>


    <!-- glow -->

    <filter
        id="glow"
        x="-50%"
        y="-50%"
        width="200%"
        height="200%"
    >

        <feGaussianBlur
            stdDeviation="12"
            result="blur"
        />

        <feMerge>

            <feMergeNode in="blur"/>

            <feMergeNode in="SourceGraphic"/>

        </feMerge>

    </filter>


    <!-- moving light -->

    <linearGradient
        id="shine"
        x1="0"
        y1="0"
        x2="1"
        y2="0"
    >

        <stop
            offset="0%"
            stop-color="#FFFFFF"
            stop-opacity="0"
        />

        <stop
            offset="50%"
            stop-color="#FFFFFF"
            stop-opacity="0.28"
        />

        <stop
            offset="100%"
            stop-color="#FFFFFF"
            stop-opacity="0"
        />

        <animate
            attributeName="x1"
            values="-1;1"
            dur="5s"
            repeatCount="indefinite"
        />

        <animate
            attributeName="x2"
            values="0;2"
            dur="5s"
            repeatCount="indefinite"
        />

    </linearGradient>


    {create_planet(theme, index)}

</defs>


<!-- soft purple glow behind card -->

<rect
    x="15"
    y="15"
    width="1070"
    height="220"
    rx="30"
    fill="{theme['b']}"
    opacity="0.12"
    filter="url(#glow)"
/>


<!-- glass card -->

<rect
    x="20"
    y="20"
    width="1060"
    height="210"
    rx="28"
    fill="url(#glass)"
    stroke="#FFFFFF"
    stroke-opacity="0.20"
    stroke-width="1.5"
/>


<!-- moving shine -->

<rect
    x="20"
    y="20"
    width="1060"
    height="210"
    rx="28"
    fill="url(#shine)"
    opacity="0.35"
/>


<!-- stars -->

{create_stars()}


<!-- planet -->

<g>

    {create_planet(theme, index)}

    <animateTransform
        attributeName="transform"
        type="translate"
        values="0 0; 0 -4; 0 0"
        dur="4s"
        repeatCount="indefinite"
    />

</g>


<!-- repository name -->

<text
    x="320"
    y="73"
    font-family="Georgia, serif"
    font-size="27"
    font-weight="bold"
    fill="#FFFFFF"
>
    {esc(name)}
</text>


<!-- description -->

<text
    x="320"
    y="110"
    font-family="Arial, sans-serif"
    font-size="17"
    fill="#E8DEF7"
>
    {esc(description)}
</text>


<!-- language -->

<text
    x="320"
    y="153"
    font-family="Arial, sans-serif"
    font-size="13"
    fill="#D9C8F5"
>
    ◈ {esc(language)}
</text>


<!-- topics -->

{topic_svg}


<!-- update -->

<text
    x="1040"
    y="55"
    text-anchor="end"
    font-family="Arial, sans-serif"
    font-size="12"
    fill="#D9C8F5"
>
    {updated}
</text>


<!-- stars -->

<text
    x="900"
    y="150"
    text-anchor="middle"
    font-family="Arial, sans-serif"
    font-size="20"
    fill="#FFFFFF"
>
    ☆
</text>

<text
    x="900"
    y="177"
    text-anchor="middle"
    font-family="Arial, sans-serif"
    font-size="12"
    fill="#CFC1E9"
>
    {stars} stars
</text>


<!-- forks -->

<text
    x="1000"
    y="150"
    text-anchor="middle"
    font-family="Arial, sans-serif"
    font-size="20"
    fill="#FFFFFF"
>
    ⑂
</text>

<text
    x="1000"
    y="177"
    text-anchor="middle"
    font-family="Arial, sans-serif"
    font-size="12"
    fill="#CFC1E9"
>
    {forks} forks
</text>


</svg>
"""

    return card


# ============================================================
# GENERATE ALL CARDS
# ============================================================

generated_files = []

for index, repo in enumerate(repositories):

    filename = (
        slugify(repo["name"])
        + ".svg"
    )

    path = os.path.join(
        REPO_DIR,
        filename
    )

    card = create_card(
        repo,
        index
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(card)

    generated_files.append(
        (
            repo,
            filename
        )
    )


# ============================================================
# BUILD README REPOSITORY SECTION
# ============================================================

repository_section = []

for repo, filename in generated_files:

    repo_url = repo["html_url"]

    repository_section.append(
        f"""
<div align="center">

<a href="{repo_url}">

<img
src="./assets/repos/{filename}"
width="100%"
alt="{esc(repo['name'])}"
/>

</a>

</div>

<br>
"""
    )


repository_html = "\n".join(
    repository_section
)


# ============================================================
# READ README
# ============================================================

with open(
    README_FILE,
    "r",
    encoding="utf-8"
) as file:

    readme = file.read()


# ============================================================
# INSERT REPOSITORIES
# ============================================================

repo_start = "<!-- REPOSITORIES:START -->"
repo_end = "<!-- REPOSITORIES:END -->"


if repo_start not in readme:

    raise RuntimeError(
        "REPOSITORIES:START marker missing."
    )

if repo_end not in readme:

    raise RuntimeError(
        "REPOSITORIES:END marker missing."
    )


start = readme.index(
    repo_start
)

end = readme.index(
    repo_end
)


readme = (
    readme[:start]
    + repo_start
    + "\n\n"
    + repository_html
    + "\n"
    + repo_end
    + readme[end + len(repo_end):]
)


# ============================================================
# RECENT SIGNALS
# ============================================================

recent = repositories[:3]

recent_lines = []

for repo in recent:

    recent_lines.append(
        f"""
<a href="{repo['html_url']}">
<b>✦ {esc(repo['name'])}</b>
</a>
&nbsp; · &nbsp;
{time_ago(repo['updated_at'])}
"""
    )


recent_html = "<br><br>".join(
    recent_lines
)


if RECENT_START not in readme:

    raise RuntimeError(
        "RECENT:START marker missing."
    )

if RECENT_END not in readme:

    raise RuntimeError(
        "RECENT:END marker missing."
    )


start = readme.index(
    RECENT_START
)

end = readme.index(
    RECENT_END
)


readme = (
    readme[:start]
    + RECENT_START
    + "\n\n"
    + recent_html
    + "\n\n"
    + RECENT_END
    + readme[end + len(RECENT_END):]
)


# ============================================================
# SAVE README
# ============================================================

with open(
    README_FILE,
    "w",
    encoding="utf-8"
) as file:

    file.write(readme)


print(
    f"🌌 Generated {len(repositories)} animated repository cards."
)
