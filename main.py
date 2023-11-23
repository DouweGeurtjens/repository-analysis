import json
import os
from pathlib import (Path)
import subprocess
from papercode.TypeErrors.TypeAnnotationCounter import count_type_annotations

from dotenv import load_dotenv
from git import (Repo)
import matplotlib.pyplot as plt
import requests
from tqdm import (tqdm)

load_dotenv('.env.local')

TOKEN = os.getenv('TOKEN')
PATH_TO_REPOS = Path('./repos')
PATH_TO_ANALYSIS_RESULTS = Path('./analysis-results')
PATH_TO_ANALYSIS_RESULTS_PAPER = Path('./analysis-results-paper')


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
        print(TOKEN)
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

            headers = {'Authorization': f'token {TOKEN}'}
            payload = {'state': 'closed', 'labels': 'bug'}
            bugs = []

            r = requests.get(f"https://api.github.com/repos/{name}/issues",
                             params=payload,
                             headers=headers)
            bugs.extend(r.json())

            while 'next' in r.links:
                next_url = r.links['next']['url']
                r = requests.get(next_url, headers=headers)
                bugs.extend(r.json())

            # Write the entire JSON response to a file so we don't have to repull stuff from GitHub constantly
            with open(f'analysis-results/{id}/issues.json', 'w') as of:
                j = json.dumps(bugs)
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
                            j = json.load(bf)
                            bugs.append(len(j))
            except (FileNotFoundError):
                pass

        x = range(len(typedness_ratios))
        fig, (ax1, ax2) = plt.subplots(1, 2)
        l = []
        ll = []
        for i in typedness_ratios:
            if i == 0:
                l.append(i)
            else:
                ll.append(i)
        print(len(l))
        print(len(ll))
        ax1.scatter(x,
                    typedness_ratios,
                    c=['r' if i == 0 else 'b' for i in typedness_ratios])
        ax2.scatter(bugs, typedness_ratios)

        # plt.scatter(x,
        #             typedness_ratios,
        #             c=['r' if i == 0 else 'b' for i in typedness_ratios])
        plt.show()


def paper_typedness_analysis():
    with open('data/results.json') as f:
        results = json.load(f)
        repos = results['items']

        for repo in tqdm(repos):
            id = repo['id']

            # Bricks on this
            if id == 3992617:
                continue

            # Only analyse if cloned
            if Path(f"repos/{id}") not in PATH_TO_REPOS.iterdir():
                continue

            if Path(f"analysis-results-paper/{id}"
                    ) in PATH_TO_ANALYSIS_RESULTS_PAPER.iterdir():
                continue

            # See https://github.com/python/mypy/issues/3717 for semantics of the report generated

            number_param_types, number_return_types, number_variable_types, number_non_param_types, number_non_return_types, number_non_variable_types = count_type_annotations(
                f"./repos/{id}")
            dump = json.dumps(
                {
                    'number_param_types': number_param_types,
                    'number_return_types': number_return_types,
                    'number_variable_types': number_variable_types,
                    'number_non_param_types': number_non_param_types,
                    'number_non_return_types': number_non_return_types,
                    'number_non_variable_types': number_non_variable_types
                },
                indent=4)
            os.makedirs(os.path.dirname(
                f'analysis-results-paper/{id}/paperanalysis.json'),
                        exist_ok=True)
            with open(f'analysis-results-paper/{id}/paperanalysis.json',
                      'w') as of:
                of.write(dump)

    return None


def basic_plots_paper():
    with open('data/results.json') as f:
        results = json.load(f)
        repos = results['items']

        typedness_ratios = []
        bugs = []
        x = []

        for repo in tqdm(repos):
            id = repo['id']

            # Only plot if analysed
            if Path(f"analysis-results-paper/{id}"
                    ) not in PATH_TO_ANALYSIS_RESULTS_PAPER.iterdir():
                continue

            try:
                with open(f'analysis-results-paper/{id}/paperanalysis.json'
                          ) as lcf:
                    ob = json.load(lcf)
                    total = ob["number_param_types"] + ob[
                        "number_return_types"] + ob[
                            "number_variable_types"] + ob[
                                "number_non_param_types"] + ob[
                                    "number_non_return_types"] + ob[
                                        "number_non_variable_types"]
                    typed = ob["number_param_types"] + ob[
                        "number_return_types"] + ob["number_variable_types"]
                    if total != 0:
                        ratio = (int(typed) / int(total)) * 100
                        typedness_ratios.append(ratio)
                        x.append(repo['name'])
            except (FileNotFoundError):
                pass

        x = range(len(typedness_ratios))
        fig, (ax1, ax2) = plt.subplots(1, 2)
        l = []
        ll = []
        for i in typedness_ratios:
            if i <= 5:
                l.append(i)
            else:
                ll.append(i)
        print(len(l))
        print(len(ll))
        ax1.scatter(x,
                    typedness_ratios,
                    c=['r' if i == 0 else 'b' for i in typedness_ratios])
        # ax2.scatter(bugs, typedness_ratios)

        # plt.scatter(x,
        #             typedness_ratios,
        #             c=['r' if i == 0 else 'b' for i in typedness_ratios])
        plt.show()


def results_union():
    union = set()
    with open('data/results.json') as f:
        results = json.load(f)
        repos = results['items']
        for repo in repos:
            union.add(repo['name'].lower())
    with open('miner/filtered-results/res.json') as f2:
        results2 = json.load(f2)
        for repo in results2:
            union.add(repo.lower())
    with open('all_included_repos_1.json', 'w') as f3:
        print(len(union))
        f3.write(json.dumps(list(union)))


def main() -> None:
    # clone_repos()
    # mypy_typedness_analysis()
    # paper_typedness_analysis()
    # get_bug_issues()
    # basic_plots()
    # results_union()
    basic_plots_paper()


if __name__ == '__main__':
    results_union()
    # main()