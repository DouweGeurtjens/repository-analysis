import json
from pathlib import (Path)

from git import (Repo)
from tqdm import (tqdm)

PATH_TO_REPOS = Path('./repos')


def clone_repos() -> None:
    with open('data/results.json') as f:
        results = json.load(f)
        repos = results['items']

        for repo in tqdm(repos):
            id = repo['id']
            name = repo['name']

            # Only clone if not already cloned
            if Path(f"repos/{id}") in PATH_TO_REPOS.iterdir():
                continue

            Repo.clone_from(f"https://github.com/{name}", f"repos/{id}")
            print(repo['id'])


def main() -> None:
    # General outline
    #   Clone repos according to results from https://seart-ghs.si.usi.ch/
    #   For each repo, use GitHub API to find several commit hashes based on their relative commit number
    #   Use GitPython to checkout each commit and run some analysis on the typedness of a repository
    #   Try to make an initial classification of the type of repository (typehinting vs no typehinting)
    #   Evidently, this naive method of classification is not exhaustive but serves as a rough initial outline
    clone_repos()


main()