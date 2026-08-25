import json
import os
import urllib.request
from datetime import datetime


USERNAME = "aditi-0926"

README_FILE = "README.md"

START_MARKER = "<!-- GALAXY:START -->"
END_MARKER = "<!-- GALAXY:END -->"


def get_repositories():

    url = (
        f"https://api.github.com/users/"
        f"{USERNAME}/repos?per_page=100&sort=updated"
    )

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Aditi-Galaxy-Portfolio"
        }
    )

    with urllib.request.urlopen(request) as response:

        return json.loads(
            response.read().decode("utf-8")
        )


def get_language_icon(language):

    icons = {

        "Python": "🐍",
        "JavaScript": "⚡",
        "TypeScript": "🔷",
        "C++": "⚙️",
        "Java": "☕",
        "HTML": "🌐",
        "CSS": "🎨",
        "Jupyter Notebook": "📓"

    }

    return icons.get(language, "✦")


def create_card(repo):

    name = repo["name"]

    description = (
        repo["description"]
        or "A project exploring technology, creativity and problem solving."
    )

    language = (
        repo["language"]
        or "Project"
    )

    stars = repo["stargazers_count"]

    forks = repo["forks_count"]

    url = repo["html_url"]

    icon = get_language_icon(language)

    return f"""
<table>
<tr>

<td width="50%">

### {icon} [{name}]({url})

{description}

**`{language}`**

⭐ {stars} &nbsp;&nbsp; 🍴 {forks}

</td>

</tr>
</table>
"""


def generate_repository_section(repositories):

    # Remove forks
    repositories = [
        repo
        for repo in repositories
        if not repo["fork"]
    ]

    # Sort by stars first
    repositories.sort(
        key=lambda repo: (
            repo["stargazers_count"],
            repo["updated_at"]
        ),
        reverse=True
    )

    # Display maximum 6 projects
    repositories = repositories[:6]

    cards = []

    for repo in repositories:

        cards.append(
            create_card(repo)
        )

    timestamp = datetime.utcnow().strftime(
        "%Y-%m-%d %H:%M UTC"
    )

    output = f"""
<div align="center">

### ✦ Projects drifting through my galaxy ✦

</div>

{''.join(cards)}

<div align="center">

<sub>
🌌 Automatically synchronized with GitHub · Updated {timestamp}
</sub>

</div>
"""

    return output.strip()


def update_readme(repository_section):

    with open(
        README_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        readme = file.read()

    start = readme.find(
        START_MARKER
    )

    end = readme.find(
        END_MARKER
    )

    if start == -1 or end == -1:

        raise RuntimeError(
            "Galaxy markers were not found in README.md"
        )

    new_readme = (
        readme[:start + len(START_MARKER)]
        + "\n\n"
        + repository_section
        + "\n\n"
        + readme[end:]
    )

    with open(
        README_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(new_readme)


def main():

    print(
        f"🌌 Scanning {USERNAME}'s GitHub universe..."
    )

    repositories = get_repositories()

    print(
        f"Found {len(repositories)} repositories."
    )

    repository_section = (
        generate_repository_section(
            repositories
        )
    )

    update_readme(
        repository_section
    )

    print(
        "✨ README.md successfully updated."
    )


if __name__ == "__main__":

    main()
