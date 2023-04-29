import json
import os
from pathlib import (Path)
import subprocess

from git import (Repo)
import matplotlib.pyplot as plt
import requests
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

            # Mypy bricks on this repo, as in it keeps going until my PC runs out of memory
            if id == 3992617:
                continue

            # Only analyse if cloned
            if Path(f"repos/{id}") not in PATH_TO_REPOS.iterdir():
                continue

            # if Path(f"analysis-results/{id}"
            #         ) in PATH_TO_ANALYSIS_RESULTS.iterdir():
            #     continue

            # See https://github.com/python/mypy/issues/3717 for semantics of the report generated
            try:
                subprocess.check_output([
                    "mypy", f"./repos/{id}", "--linecount-report",
                    f"./analysis-results/{id}/"
                ])
                subprocess.run(["touch", f"./analysis-results/{id}/SUCCESS"])
            except subprocess.CalledProcessError as e:
                # If we fail because of a syntax error, the repository should not be included in the analysis
                # Reason being that syntax errors indicate that the repository is probably not maintained any longer
                # We mark the repositories by creating an empty file in the respective analysis-results folder
                if "[syntax]" in e.output.decode():
                    subprocess.run(
                        ["touch", f"./analysis-results/{id}/SYNTAX_ERROR"])


def get_bug_issues() -> None:
    with open('data/results.json') as f:
        results = json.load(f)
        repos = results['items']

        for repo in tqdm(repos):
            id = repo['id']
            name = repo['name']

            # If Mypy didn't produce an output file for the repo we don't bother getting the issues
            if not os.path.isfile(f"analysis-results/{id}/linecount.txt"):
                continue

            # Skip any repos with syntax errors
            if os.path.isfile(f"analysis-results/{id}/SYNTAX_ERROR"):
                continue

            payload = {'state': 'closed', 'labels': 'bug'}
            r = requests.get(f"https://api.github.com/repos/{name}/issues",
                             params=payload)

            # Write the entire JSON response to a file so we don't have to repull stuff from GitHub constantly
            with open(f'analysis-results/{id}/issues.json', 'w') as of:
                j = json.dumps(r.json())
                of.write(j)


def basic_plots() -> None:
    with open('data/results.json') as f:
        results = json.load(f)
        repos = results['items']

        typedness_ratios = []
        bugs = []
        x = []

        for repo in tqdm(repos):
            id = repo['id']

            # Only plot if analysed
            if Path(f"analysis-results/{id}"
                    ) not in PATH_TO_ANALYSIS_RESULTS.iterdir():
                continue

            # Skip any repos with syntax errors
            if os.path.isfile(f"analysis-results/{id}/SYNTAX_ERROR"):
                continue

            try:
                with open(f'analysis-results/{id}/linecount.txt') as lcf:
                    lines = lcf.readlines()
                    first_line = lines[0]
                    values = first_line.split()
                    total_lines = values[0]
                    annotated_lines = values[2]

                    if int(total_lines) != 0:
                        ratio = (int(annotated_lines) / int(total_lines)) * 100
                        typedness_ratios.append(ratio)
                        x.append(repo['name'])

                with open(f'analysis-results/{id}/issues.json') as bf:
                    r = json.loads(bf)
                    bugs.append(len(r))
            except (FileNotFoundError):
                pass

        # x = range(len(typedness_ratios))
        fig1, ax1 = plt.subplot().scatter(
            x,
            typedness_ratios,
            c=['r' if i == 0 else 'b' for i in typedness_ratios])

        fig2, ax2 = plt.subplot().scatter(typedness_ratios, bugs)

        # plt.scatter(x,
        #             typedness_ratios,
        #             c=['r' if i == 0 else 'b' for i in typedness_ratios])
        plt.show()


def main() -> None:
    # clone_repos()
    # mypy_typedness_analysis()
    get_bug_issues()
    basic_plots()


main()