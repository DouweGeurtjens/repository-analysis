import json
import os
from pathlib import (Path)
import subprocess

from git import (Repo)
import matplotlib.pyplot as plt
from tqdm import (tqdm)

PATH_TO_REPOS = Path('./repos')
PATH_TO_ANALYSIS_RESULTS = Path('./analysis-results')


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


def mypy_typedness_analysis() -> None:
    with open('data/results.json') as f:
        results = json.load(f)
        repos = results['items']

        for repo in tqdm(repos):
            id = repo['id']

            # Mypy bricks on this repo
            if id == 3992617:
                continue
            # Only analyse if cloned
            if Path(f"repos/{id}") not in PATH_TO_REPOS.iterdir():
                continue

            # if Path(f"analysis-results/{id}"
            #         ) in PATH_TO_ANALYSIS_RESULTS.iterdir():
            #     continue

            # See https://github.com/python/mypy/issues/3717 for semantics of the report generated
            proc = subprocess.run([
                "mypy", f"./repos/{id}", "--linecount-report",
                f"./analysis-results/{id}/"
            ])


def basic_plots() -> None:
    with open('data/results.json') as f:
        results = json.load(f)
        repos = results['items']

        typedness_ratios = []
        x = []

        for repo in tqdm(repos):
            id = repo['id']

            # Only plot if analysed
            if Path(f"analysis-results/{id}"
                    ) not in PATH_TO_ANALYSIS_RESULTS.iterdir():
                continue
            try:
                with open(f'analysis-results/{id}/linecount.txt') as f:
                    lines = f.readlines()
                    first_line = lines[0]
                    values = first_line.split()
                    total_lines = values[0]
                    annotated_lines = values[2]

                    if int(total_lines) != 0:
                        ratio = (int(annotated_lines) / int(total_lines)) * 100
                        typedness_ratios.append(ratio)
            except (FileNotFoundError):
                pass

        x = range(len(typedness_ratios))
        plt.scatter(x,
                    typedness_ratios,
                    c=['r' if i == 0 else 'b' for i in typedness_ratios])
        plt.show()


def main() -> None:
    # General outline
    #   Clone repos according to results from https://seart-ghs.si.usi.ch/
    #   For each repo, use GitHub API to find several commit hashes based on their relative commit number
    #   Use GitPython to checkout each commit and run some analysis on the typedness of a repository
    #   Try to make an initial classification of the type of repository (typehinting vs no typehinting)
    #   Evidently, this naive method of classification is not exhaustive but serves as a rough initial outline
    clone_repos()
    mypy_typedness_analysis()
    basic_plots()


main()