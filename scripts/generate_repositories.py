import os
import html
import math
import requests
from datetime import datetime


USERNAME = "aditi-0926"

SVG_FILE = "assets/galaxy.svg"
README_FILE = "README.md"

RECENT_START = "<!-- RECENT:START -->"
RECENT_END = "<!-- RECENT:END -->"


# =========================================================
# GITHUB API
# =========================================================

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


# =========================================================
# REMOVE FORKS
# =========================================================

repositories = [
    repo for repo in repositories
    if not repo["fork"]
]


# =========================================================
# SORT BY MOST RECENTLY UPDATED
# =========================================================

repositories.sort(
    key=lambda repo: repo["updated_at"],
    reverse=True
)


# =========================================================
# PLANETS
# =========================================================

PLANETS = [
    {
        "gradient1": "#5B7CFF",
        "gradient2": "#9B7CFF",
        "ring": "#BCA7FF"
    },
    {
        "gradient1": "#8B5CF6",
        "gradient2": "#F0ABFC",
        "ring": "#E9D5FF"
    },
    {
        "gradient1": "#C4B5FD",
        "gradient2": "#64748B",
        "ring": "#E2E8F0"
    },
    {
        "gradient1": "#D946EF",
        "gradient2": "#6366F1",
        "ring": "#E879F9"
    },
    {
        "gradient1": "#38BDF8",
        "gradient2": "#818CF8",
        "ring": "#BAE6FD"
    },
    {
        "gradient1": "#A78BFA",
        "gradient2": "#4F46E5",
        "ring": "#C4B5FD"
    }
]


# =========================================================
# SVG HELPERS
# =========================================================

def esc(value):
    return html.escape(str(value))


def shorten(text, length=105):

    text = text or "A little world still waiting to be explored."

    if len(text) <= length:
        return text

    return text[:length - 3] + "..."


def format_date(date_string):

    date = datetime.strptime(
        date_string,
        "%Y-%m-%dT%H:%M:%SZ"
    )

    return date.strftime("%d %b %Y")


def time_ago(date_string):

    date = datetime.strptime(
        date_string,
        "%Y-%m-%dT%H:%M:%SZ"
    )

    now = datetime.utcnow()

    seconds = int(
        (now - date).total_seconds()
    )

    if seconds < 86400:
        hours = max(1, seconds // 3600)
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


# =========================================================
# STAR FIELD
# =========================================================

def create_stars():

    stars = []

    for i in range(150):

        x = (i * 137) % 1200
        y = (i * 79) % 2200

        radius = [
            1,
            1,
            1.2,
            1.5,
            2
        ][i % 5]

        opacity = [
            0.35,
            0.45,
            0.6,
            0.8,
            0.95
        ][i % 5]

        stars.append(
            f"""
            <circle
                cx="{x}"
                cy="{y}"
                r="{radius}"
                fill="#FFFFFF"
                opacity="{opacity}"
            />
            """
        )

    return "\n".join(stars)


# =========================================================
# PLANET
# =========================================================

def create_planet(index, cx, cy):

    planet = PLANETS[
        index % len(PLANETS)
    ]

    gradient_id = f"planetGradient{index}"

    return f"""
    <defs>

        <radialGradient id="{gradient_id}">

            <stop
                offset="0%"
                stop-color="#FFFFFF"
                stop-opacity="0.9"
            />

            <stop
                offset="30%"
                stop-color="{planet['gradient1']}"
            />

            <stop
                offset="100%"
                stop-color="{planet['gradient2']}"
            />

        </radialGradient>

    </defs>

    <ellipse
        cx="{cx}"
        cy="{cy}"
        rx="76"
        ry="22"
        fill="none"
        stroke="{planet['ring']}"
        stroke-width="3"
        opacity="0.45"
        transform="rotate(-18 {cx} {cy})"
    />

    <circle
        cx="{cx}"
        cy="{cy}"
        r="56"
        fill="url(#{gradient_id})"
        opacity="0.95"
    />

    <circle
        cx="{cx - 18}"
        cy="{cy - 17}"
        r="10"
        fill="#FFFFFF"
        opacity="0.12"
    />

    <circle
        cx="{cx + 20}"
        cy="{cy + 18}"
        r="16"
        fill="#000000"
        opacity="0.10"
    />
    """


# =========================================================
# REPOSITORY CARD
# =========================================================

def create_card(repo, index, y):

    name = repo["name"]

    description = shorten(
        repo["description"]
    )

    language = repo["language"] or "Unknown"

    stars = repo["stargazers_count"]

    forks = repo["forks_count"]

    url = repo["html_url"]

    updated = time_ago(
        repo["updated_at"]
    )

    topics = repo.get(
        "topics",
        []
    )[:4]

    x = 70

    width = 1060

    height = 210

    planet_x = 155

    planet_y = y + 105

    card_gradient = f"cardGradient{index}"

    topic_elements = []

    topic_x = 280

    for topic in topics:

        topic_width = max(
            75,
            len(topic) * 8 + 30
        )

        topic_elements.append(
            f"""
            <rect
                x="{topic_x}"
                y="{y + 157}"
                width="{topic_width}"
                height="28"
                rx="14"
                fill="#8B6FCB"
                opacity="0.28"
            />

            <text
                x="{topic_x + topic_width / 2}"
                y="{y + 176}"
                text-anchor="middle"
                font-family="Arial, sans-serif"
                font-size="12"
                fill="#E9DDFF"
            >
                {esc(topic)}
            </text>
            """
        )

        topic_x += topic_width + 10


    return f"""
    <defs>

        <linearGradient
            id="{card_gradient}"
            x1="0"
            y1="0"
            x2="1"
            y2="1"
        >

            <stop
                offset="0%"
                stop-color="#FFFFFF"
                stop-opacity="0.13"
            />

            <stop
                offset="45%"
                stop-color="#7C5CBA"
                stop-opacity="0.11"
            />

            <stop
                offset="100%"
                stop-color="#0A071D"
                stop-opacity="0.68"
            />

        </linearGradient>

        <filter
            id="glow{index}"
            x="-50%"
            y="-50%"
            width="200%"
            height="200%"
        >

            <feGaussianBlur
                stdDeviation="9"
                result="blur"
            />

            <feMerge>

                <feMergeNode
                    in="blur"
                />

                <feMergeNode
                    in="SourceGraphic"
                />

            </feMerge>

        </filter>

    </defs>


    <a
        href="{esc(url)}"
        target="_blank"
    >

        <!-- soft outer glow -->

        <rect
            x="{x - 4}"
            y="{y - 4}"
            width="{width + 8}"
            height="{height + 8}"
            rx="28"
            fill="#9B7CFF"
            opacity="0.08"
            filter="url(#glow{index})"
        />


        <!-- glass card -->

        <rect
            x="{x}"
            y="{y}"
            width="{width}"
            height="{height}"
            rx="25"
            fill="url(#{card_gradient})"
            stroke="#BBA8FF"
            stroke-opacity="0.22"
            stroke-width="1.5"
        />


        <!-- planet -->

        {create_planet(
            index,
            planet_x,
            planet_y
        )}


        <!-- repository name -->

        <text
            x="280"
            y="{y + 62}"
            font-family="Georgia, serif"
            font-size="27"
            font-weight="bold"
            fill="#F7F1FF"
        >

            {esc(name)}

        </text>


        <!-- description -->

        <text
            x="280"
            y="{y + 96}"
            font-family="Arial, sans-serif"
            font-size="14"
            fill="#D8CFEA"
        >

            {esc(description)}

        </text>


        <!-- language -->

        <text
            x="280"
            y="{y + 134}"
            font-family="Arial, sans-serif"
            font-size="13"
            fill="#BFAFE3"
        >

            ◈ {esc(language)}

        </text>


        <!-- topics -->

        {''.join(topic_elements)}


        <!-- updated -->

        <text
            x="1050"
            y="{y + 45}"
            text-anchor="end"
            font-family="Arial, sans-serif"
            font-size="12"
            fill="#B8A5E7"
        >

            updated {updated}

        </text>


        <!-- stars -->

        <text
            x="900"
            y="{y + 125}"
            text-anchor="middle"
            font-family="Arial, sans-serif"
            font-size="14"
            fill="#F2E9FF"
        >

            ☆ {stars}

        </text>


        <text
            x="900"
            y="{y + 147}"
            text-anchor="middle"
            font-family="Arial, sans-serif"
            font-size="11"
            fill="#AFA2C8"
        >

            stars

        </text>


        <!-- forks -->

        <text
            x="990"
            y="{y + 125}"
            text-anchor="middle"
            font-family="Arial, sans-serif"
            font-size="14"
            fill="#F2E9FF"
        >

            ♧ {forks}

        </text>


        <text
            x="990"
            y="{y + 147}"
            text-anchor="middle"
            font-family="Arial, sans-serif"
            font-size="11"
            fill="#AFA2C8"
        >

            forks

        </text>


    </a>
    """


# =========================================================
# CREATE GALAXY SVG
# =========================================================

card_spacing = 235

top = 80

height = top + (
    len(repositories) * card_spacing
) + 80


cards = []

for index, repo in enumerate(repositories):

    y = top + (
        index * card_spacing
    )

    cards.append(
        create_card(
            repo,
            index,
            y
        )
    )


svg = f"""<svg
xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink"
width="1200"
height="{height}"
viewBox="0 0 1200 {height}"
>

<defs>

    <linearGradient
        id="background"
        x1="0"
        y1="0"
        x2="0"
        y2="1"
    >

        <stop
            offset="0%"
            stop-color="#03051A"
        />

        <stop
            offset="45%"
            stop-color="#100A2C"
        />

        <stop
            offset="75%"
            stop-color="#24104F"
        />

        <stop
            offset="100%"
            stop-color="#08051C"
        />

    </linearGradient>


    <radialGradient
        id="nebula"
    >

        <stop
            offset="0%"
            stop-color="#A78BFA"
            stop-opacity="0.30"
        />

        <stop
            offset="45%"
            stop-color="#7C3AED"
            stop-opacity="0.10"
        />

        <stop
            offset="100%"
            stop-color="#000000"
            stop-opacity="0"
        />

    </radialGradient>


    <filter
        id="nebulaBlur"
        x="-50%"
        y="-50%"
        width="200%"
        height="200%"
    >

        <feGaussianBlur
            stdDeviation="45"
        />

    </filter>

</defs>


<!-- BACKGROUND -->

<rect
    width="1200"
    height="{height}"
    fill="url(#background)"
/>


<!-- NEBULA CLOUDS -->

<ellipse
    cx="170"
    cy="500"
    rx="350"
    ry="220"
    fill="url(#nebula)"
    filter="url(#nebulaBlur)"
/>

<ellipse
    cx="1030"
    cy="1050"
    rx="400"
    ry="260"
    fill="url(#nebula)"
    filter="url(#nebulaBlur)"
/>

<ellipse
    cx="550"
    cy="{height - 300}"
    rx="450"
    ry="250"
    fill="url(#nebula)"
    filter="url(#nebulaBlur)"
/>


<!-- STARS -->

{create_stars()}


<!-- GALAXY TITLE -->

<text
    x="600"
    y="42"
    text-anchor="middle"
    font-family="Georgia, serif"
    font-size="24"
    letter-spacing="6"
    fill="#D8C5FF"
>

✦  MY REPOSITORY GALAXY  ✦

</text>


<!-- REPOSITORIES -->

{''.join(cards)}


<!-- FOOTER -->

<text
    x="600"
    y="{height - 35}"
    text-anchor="middle"
    font-family="Georgia, serif"
    font-size="14"
    letter-spacing="3"
    fill="#BBA8E8"
>

✦ every repository is a little universe ✦

</text>

</svg>
"""


# =========================================================
# SAVE SVG
# =========================================================

os.makedirs(
    "assets",
    exist_ok=True
)

with open(
    SVG_FILE,
    "w",
    encoding="utf-8"
) as f:

    f.write(svg)


print(
    f"🌌 Generated galaxy with "
    f"{len(repositories)} repositories."
)


# =========================================================
# UPDATE RECENT SIGNALS
# =========================================================

recent = repositories[:3]

recent_lines = []

for repo in recent:

    name = repo["name"]

    url = repo["html_url"]

    updated = time_ago(
        repo["updated_at"]
    )

    recent_lines.append(
        f'✦ <a href="{url}"><b>{esc(name)}</b></a> '
        f'&nbsp; · &nbsp; {updated}'
    )


recent_html = "<br><br>".join(
    recent_lines
)


with open(
    README_FILE,
    "r",
    encoding="utf-8"
) as f:

    readme = f.read()


start = readme.find(
    RECENT_START
)

end = readme.find(
    RECENT_END
)


if start == -1 or end == -1:

    raise RuntimeError(
        "Recent signal markers not found."
    )


new_readme = (
    readme[:start + len(RECENT_START)]
    + "\n\n"
    + recent_html
    + "\n\n"
    + readme[end:]
)


with open(
    README_FILE,
    "w",
    encoding="utf-8"
) as f:

    f.write(new_readme)


print("✨ Recent signals updated.")
