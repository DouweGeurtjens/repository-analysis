import pandas as pd
from patsy import dmatrices
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
import settings
from tqdm import tqdm
import json
from git import Repo
from pathlib import Path
from scipy.stats import combine_pvalues, hmean

from metrics import manage_git_checkouts


def create_summary_file(commit=None):
    duplicate_tracker = {}
    # Typedness should be the index I think, not sure
    with open(settings.ALL_INCLUDED_REPOS_JSON) as f:
        repos = json.load(f)
        ids = []
        typedness = []
        bugs = []
        commits = []
        sloccount = []
        issuecount = []

        for id, repo_name in enumerate(tqdm(repos)):
            # TODO There are some issues with duplicates ugh
            if repo_name.lower() not in duplicate_tracker:
                duplicate_tracker[repo_name.lower()] = True
            else:
                continue

            path_to_repo = settings.PATH_TO_REPOS.joinpath(Path(str(id)))
            analysis_results_path = settings.PATH_TO_ANALYSIS_RESULTS.joinpath(
                str(id))
            issues_path = settings.PATH_TO_ISSUES.joinpath(str(id))

            ok, repo, checked_out_commit = manage_git_checkouts(
                path_to_repo, id, commit)

            if not ok:
                continue

            path_to_analysis_results_dir_for_repo = settings.PATH_TO_ANALYSIS_RESULTS.joinpath(
                Path(str(id)))

            path_to_typedness_results_file = path_to_analysis_results_dir_for_repo.joinpath(
                Path(f'typedness_{checked_out_commit}.json'))
            path_to_sloccount_results_file = path_to_analysis_results_dir_for_repo.joinpath(
                Path(f'sloccount_{checked_out_commit}.json'))
            path_to_total_issues_results_file = path_to_analysis_results_dir_for_repo.joinpath(
                Path(f'total_issues_{checked_out_commit}.json'))
            path_to_bug_issues_results_file = path_to_analysis_results_dir_for_repo.joinpath(
                Path(f'bug_issues_{checked_out_commit}.json'))

            # Only do the rest if all folders exist
            if analysis_results_path not in settings.PATH_TO_ANALYSIS_RESULTS.iterdir(
            ):
                continue
            # Make sure the actual files also exist
            if path_to_typedness_results_file not in analysis_results_path.iterdir(
            ):
                continue
            if path_to_sloccount_results_file not in analysis_results_path.iterdir(
            ):
                continue
            if path_to_total_issues_results_file not in analysis_results_path.iterdir(
            ):
                continue
            if path_to_bug_issues_results_file not in analysis_results_path.iterdir(
            ):
                continue

            # Count total amount of commits
            total_commits_for_repo = 0
            for i in repo.iter_commits():
                total_commits_for_repo += 1

            # Compute the typedness
            with open(
                    analysis_results_path.joinpath(
                        Path(f'typedness_{checked_out_commit}.json'))
            ) as typedness_file:
                typedness_data = json.load(typedness_file)
                summary = typedness_data['total']

                # The total amount of "things" that can have a type annotation
                total_possible_typedness = summary[
                    "number_param_types"] + summary[
                        "number_return_types"] + summary[
                            "number_variable_types"] + summary[
                                "number_non_param_types"] + summary[
                                    "number_non_return_types"] + summary[
                                        "number_non_variable_types"]

                # The actual amount of "things" that have a type annotation
                actual_typedness = summary["number_param_types"] + summary[
                    "number_return_types"] + summary["number_variable_types"]

                # Compute the fraction
                if total_possible_typedness != 0:
                    typedness_for_repo = (int(actual_typedness) /
                                          int(total_possible_typedness)) * 100
                else:
                    typedness_for_repo = 0

            # Get the amount of lines of codes
            with open(
                    analysis_results_path.joinpath(
                        Path(f'sloccount_{checked_out_commit}.json'))
            ) as sloccount_file:
                try:
                    sloccount_data = json.load(sloccount_file)
                except:
                    print(f'sloccount failed to decode with repo id: {id}')
                    continue
                langs = sloccount_data['languages']
                for lang in langs:
                    if lang['language'] == "Python":
                        sloccount_for_repo = lang['sourceCount']

            # Get the amount of total issues
            with open(
                    analysis_results_path.joinpath(
                        Path(f'total_issues_{checked_out_commit}.json'))
            ) as total_issues_file:
                total_issues_data = json.load(total_issues_file)
                total_issues_for_repo = total_issues_data['total_count']

            # Get the amount of bug issues
            with open(
                    analysis_results_path.joinpath(
                        Path(f'bug_issues_{checked_out_commit}.json'))
            ) as issues_file:
                bug_issues_data = json.load(issues_file)
                bugs_for_repo = bug_issues_data['bug_count']

            ids.append(id)
            typedness.append(typedness_for_repo)
            bugs.append(bugs_for_repo)
            commits.append(total_commits_for_repo)
            sloccount.append(sloccount_for_repo)
            issuecount.append(total_issues_for_repo)

    res = {
        'typedness': typedness,
        'repo': ids,
        'bugs': bugs,
        'commits': commits,
        'sloccount': sloccount,
        'issuecount': issuecount
    }

    # TODO clean this up
    with open('./testt.json', 'w') as ff:
        j = json.dumps(res, indent=4)
        ff.write(j)


def negative_binomial_regression():
    # https://timeseriesreasoning.com/contents/negative-binomial-regression-model/
    data = {}
    with open('./testt.json') as f:
        j = json.load(f)
        data['repo'] = j['repo']
        data['typedness'] = j['typedness']
        data['bugs'] = j['bugs']
        data['commits'] = j['commits']
        data['sloccount'] = j['sloccount']
        data['issuecount'] = j['issuecount']

    bugratio = []
    for i in range(len(data['bugs'])):
        bugratio.append((data['bugs'][i] / data['issuecount'][i]) * 100)

    data['bugratio'] = bugratio

    df = pd.DataFrame(data=data)
    # df.boxplot('typedness')
    # plt.show()
    # df.boxplot('bugs')
    # plt.show()
    # df.boxplot('commits')
    # plt.show()
    # df.boxplot('sloccount')
    # plt.show()
    # df.boxplot('issuecount')
    # plt.show()
    # df.boxplot('bugratio')
    # plt.show()
    # Exclude repos with 0 or exactly 2 bugs
    df = df[(df['bugs'] > 0)]
    print(df)
    print(df.describe())
    df.to_clipboard()
    train_percentage = 0.8
    starting_mask = np.random.rand(len(df)) < train_percentage
    #
    k_offset = int(len(df.index) * (1 - train_percentage))

    # masks = []
    # for i in range(int(1 / (1 - train_percentage))):
    #     starting_mask = np.roll(starting_mask, k_offset)
    #     masks.append(starting_mask)

    masks = [np.array([ True, False, False,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True, False,
        True,  True,  True,  True,  True, False,  True,  True,  True,
       False,  True,  True,  True,  True,  True, False,  True,  True,
       False, False,  True,  True,  True,  True,  True, False,  True,
        True,  True,  True,  True,  True,  True, False,  True, False,
       False, False,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True, False,  True,  True,  True,  True,
       False,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True, False,  True,  True,  True,  True, False,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True, False, False,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True, False,  True, False,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True, False, False, False, False,  True, False,  True,
        True,  True,  True, False,  True,  True,  True,  True, False,
       False,  True,  True, False,  True,  True,  True,  True,  True,
        True,  True, False,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True, False,  True,  True,
        True,  True, False,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True, False,  True, False, False,
        True,  True,  True, False,  True,  True,  True,  True, False,
        True,  True,  True,  True,  True, False,  True, False,  True,
        True,  True,  True,  True,  True, False,  True,  True,  True,
        True,  True, False, False,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True, False,  True,
        True,  True, False,  True,  True,  True,  True,  True, False,
        True, False,  True,  True,  True,  True,  True,  True,  True,
        True,  True, False,  True,  True, False,  True, False,  True,
        True,  True,  True, False,  True,  True,  True,  True,  True,
        True,  True,  True, False, False,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True, False, False,  True,  True,  True,  True, False,
        True,  True, False,  True,  True, False,  True,  True,  True,
        True,  True,  True,  True, False,  True, False, False, False,
       False,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True, False, False,
        True,  True,  True, False,  True,  True,  True,  True,  True,
        True, False,  True,  True,  True,  True,  True,  True, False,
        True,  True, False,  True,  True,  True,  True,  True,  True,
       False,  True, False,  True, False,  True, False,  True,  True,
        True,  True, False, False,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True, False,
        True,  True,  True, False,  True,  True, False,  True,  True,
        True,  True,  True,  True,  True, False,  True, False,  True,
        True, False,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True, False, False,  True,  True, False,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True, False, False,  True, False,  True,  True,
        True, False, False,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
       False,  True,  True,  True,  True,  True, False,  True, False,
        True,  True, False,  True,  True,  True, False,  True,  True,
        True,  True,  True,  True,  True, False,  True,  True,  True,
       False,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True, False,  True,  True, False,  True, False,
        True,  True,  True,  True,  True,  True,  True,  True, False,
        True,  True,  True,  True, False,  True,  True,  True, False,
       False,  True, False, False,  True, False,  True, False, False,
        True,  True,  True, False,  True,  True,  True,  True, False,
        True,  True,  True,  True,  True, False,  True,  True,  True,
        True,  True,  True,  True, False,  True,  True,  True,  True,
       False,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True, False,
       False,  True,  True,  True,  True]), np.array([ True,  True,  True, False,  True, False,  True,  True, False,
        True,  True,  True, False,  True,  True,  True,  True,  True,
        True,  True, False,  True,  True,  True, False,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
       False,  True,  True, False,  True, False,  True,  True,  True,
        True,  True,  True,  True,  True, False,  True,  True,  True,
        True, False,  True,  True,  True, False, False,  True, False,
       False,  True, False,  True, False, False,  True,  True,  True,
       False,  True,  True,  True,  True, False,  True,  True,  True,
        True,  True, False,  True,  True,  True,  True,  True,  True,
        True, False,  True,  True,  True,  True, False,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True, False, False,  True,  True,
        True,  True,  True, False, False,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True, False,  True,  True,  True,  True,  True, False,  True,
        True,  True, False,  True,  True,  True,  True,  True, False,
        True,  True, False, False,  True,  True,  True,  True,  True,
       False,  True,  True,  True,  True,  True,  True,  True, False,
        True, False, False, False,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True, False,  True,  True,
        True,  True, False,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True, False,  True,  True,  True,  True,
       False,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True, False, False,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True, False,
        True, False,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True, False, False, False, False,  True,
       False,  True,  True,  True,  True, False,  True,  True,  True,
        True, False, False,  True,  True, False,  True,  True,  True,
        True,  True,  True,  True, False,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True, False,
        True,  True,  True,  True, False,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True, False,  True,
       False, False,  True,  True,  True, False,  True,  True,  True,
        True, False,  True,  True,  True,  True,  True, False,  True,
       False,  True,  True,  True,  True,  True,  True, False,  True,
        True,  True,  True,  True, False, False,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
       False,  True,  True,  True, False,  True,  True,  True,  True,
        True, False,  True, False,  True,  True,  True,  True,  True,
        True,  True,  True,  True, False,  True,  True, False,  True,
       False,  True,  True,  True,  True, False,  True,  True,  True,
        True,  True,  True,  True,  True, False, False,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True, False, False,  True,  True,  True,
        True, False,  True,  True, False,  True,  True, False,  True,
        True,  True,  True,  True,  True,  True, False,  True, False,
       False, False, False,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
       False, False,  True,  True,  True, False,  True,  True,  True,
        True,  True,  True, False,  True,  True,  True,  True,  True,
        True, False,  True,  True, False,  True,  True,  True,  True,
        True,  True, False,  True, False,  True, False,  True, False,
        True,  True,  True,  True, False, False,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True, False,  True,  True,  True, False,  True,  True, False,
        True,  True,  True,  True,  True,  True,  True, False,  True,
       False,  True,  True, False,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True, False, False,  True,  True, False,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True, False, False,  True, False,
        True,  True,  True, False, False,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True, False,  True,  True]), np.array([ True, False,  True,  True,  True,  True,  True,  True, False,
        True, False,  True, False,  True, False,  True,  True,  True,
        True, False, False,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True, False,  True,
        True,  True, False,  True,  True, False,  True,  True,  True,
        True,  True,  True,  True, False,  True, False,  True,  True,
       False,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
       False, False,  True,  True, False,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True, False, False,  True, False,  True,  True,  True,
       False, False,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True, False,
        True,  True,  True,  True,  True, False,  True, False,  True,
        True, False,  True,  True,  True, False,  True,  True,  True,
        True,  True,  True,  True, False,  True,  True,  True, False,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True, False,  True,  True, False,  True, False,  True,
        True,  True,  True,  True,  True,  True,  True, False,  True,
        True,  True,  True, False,  True,  True,  True, False, False,
        True, False, False,  True, False,  True, False, False,  True,
        True,  True, False,  True,  True,  True,  True, False,  True,
        True,  True,  True,  True, False,  True,  True,  True,  True,
        True,  True,  True, False,  True,  True,  True,  True, False,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True, False, False,
        True,  True,  True,  True,  True, False, False,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True, False,  True,  True,  True,  True,  True,
       False,  True,  True,  True, False,  True,  True,  True,  True,
        True, False,  True,  True, False, False,  True,  True,  True,
        True,  True, False,  True,  True,  True,  True,  True,  True,
        True, False,  True, False, False, False,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True, False,
        True,  True,  True,  True, False,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True, False,  True,  True,
        True,  True, False,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True, False, False,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True, False,  True, False,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True, False, False, False,
       False,  True, False,  True,  True,  True,  True, False,  True,
        True,  True,  True, False, False,  True,  True, False,  True,
        True,  True,  True,  True,  True,  True, False,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True, False,  True,  True,  True,  True, False,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
       False,  True, False, False,  True,  True,  True, False,  True,
        True,  True,  True, False,  True,  True,  True,  True,  True,
       False,  True, False,  True,  True,  True,  True,  True,  True,
       False,  True,  True,  True,  True,  True, False, False,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True, False,  True,  True,  True, False,  True,  True,
        True,  True,  True, False,  True, False,  True,  True,  True,
        True,  True,  True,  True,  True,  True, False,  True,  True,
       False,  True, False,  True,  True,  True,  True, False,  True,
        True,  True,  True,  True,  True,  True,  True, False, False,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True, False, False,  True,
        True,  True,  True, False,  True,  True, False,  True,  True,
       False,  True,  True,  True,  True,  True,  True,  True, False,
        True, False, False, False, False,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True, False, False,  True,  True,  True, False,  True,
        True,  True,  True,  True,  True, False,  True,  True,  True,
        True,  True,  True, False,  True]), np.array([ True,  True,  True, False,  True,  True,  True,  True,  True,
       False,  True, False,  True,  True,  True,  True,  True,  True,
        True,  True,  True, False,  True,  True, False,  True, False,
        True,  True,  True,  True, False,  True,  True,  True,  True,
        True,  True,  True,  True, False, False,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True, False, False,  True,  True,  True,  True,
       False,  True,  True, False,  True,  True, False,  True,  True,
        True,  True,  True,  True,  True, False,  True, False, False,
       False, False,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True, False,
       False,  True,  True,  True, False,  True,  True,  True,  True,
        True,  True, False,  True,  True,  True,  True,  True,  True,
       False,  True,  True, False,  True,  True,  True,  True,  True,
        True, False,  True, False,  True, False,  True, False,  True,
        True,  True,  True, False, False,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
       False,  True,  True,  True, False,  True,  True, False,  True,
        True,  True,  True,  True,  True,  True, False,  True, False,
        True,  True, False,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True, False, False,  True,  True, False,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True, False, False,  True, False,  True,
        True,  True, False, False,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True, False,  True,  True,  True,  True,  True, False,  True,
       False,  True,  True, False,  True,  True,  True, False,  True,
        True,  True,  True,  True,  True,  True, False,  True,  True,
        True, False,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True, False,  True,  True, False,  True,
       False,  True,  True,  True,  True,  True,  True,  True,  True,
       False,  True,  True,  True,  True, False,  True,  True,  True,
       False, False,  True, False, False,  True, False,  True, False,
       False,  True,  True,  True, False,  True,  True,  True,  True,
       False,  True,  True,  True,  True,  True, False,  True,  True,
        True,  True,  True,  True,  True, False,  True,  True,  True,
        True, False,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
       False, False,  True,  True,  True,  True,  True, False, False,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True, False,  True,  True,  True,
        True,  True, False,  True,  True,  True, False,  True,  True,
        True,  True,  True, False,  True,  True, False, False,  True,
        True,  True,  True,  True, False,  True,  True,  True,  True,
        True,  True,  True, False,  True, False, False, False,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True, False,  True,  True,  True,  True, False,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True, False,
        True,  True,  True,  True, False,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
       False, False,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True, False,  True, False,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True, False,
       False, False, False,  True, False,  True,  True,  True,  True,
       False,  True,  True,  True,  True, False, False,  True,  True,
       False,  True,  True,  True,  True,  True,  True,  True, False,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True, False,  True,  True,  True,  True, False,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True, False,  True, False, False,  True,  True,  True,
       False,  True,  True,  True,  True, False,  True,  True,  True,
        True,  True, False,  True, False,  True,  True,  True,  True,
        True,  True, False,  True,  True,  True,  True,  True, False,
       False,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True, False]), np.array([False,  True, False,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True, False, False, False, False,
        True, False,  True,  True,  True,  True, False,  True,  True,
        True,  True, False, False,  True,  True, False,  True,  True,
        True,  True,  True,  True,  True, False,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
       False,  True,  True,  True,  True, False,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True, False,
        True, False, False,  True,  True,  True, False,  True,  True,
        True,  True, False,  True,  True,  True,  True,  True, False,
        True, False,  True,  True,  True,  True,  True,  True, False,
        True,  True,  True,  True,  True, False, False,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True, False,  True,  True,  True, False,  True,  True,  True,
        True,  True, False,  True, False,  True,  True,  True,  True,
        True,  True,  True,  True,  True, False,  True,  True, False,
        True, False,  True,  True,  True,  True, False,  True,  True,
        True,  True,  True,  True,  True,  True, False, False,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True, False, False,  True,  True,
        True,  True, False,  True,  True, False,  True,  True, False,
        True,  True,  True,  True,  True,  True,  True, False,  True,
       False, False, False, False,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True, False, False,  True,  True,  True, False,  True,  True,
        True,  True,  True,  True, False,  True,  True,  True,  True,
        True,  True, False,  True,  True, False,  True,  True,  True,
        True,  True,  True, False,  True, False,  True, False,  True,
       False,  True,  True,  True,  True, False, False,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True, False,  True,  True,  True, False,  True,  True,
       False,  True,  True,  True,  True,  True,  True,  True, False,
        True, False,  True,  True, False,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True, False, False,  True,  True, False,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True, False, False,  True,
       False,  True,  True,  True, False, False,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True, False,  True,  True,  True,  True,  True,
       False,  True, False,  True,  True, False,  True,  True,  True,
       False,  True,  True,  True,  True,  True,  True,  True, False,
        True,  True,  True, False,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True, False,  True,  True,
       False,  True, False,  True,  True,  True,  True,  True,  True,
        True,  True, False,  True,  True,  True,  True, False,  True,
        True,  True, False, False,  True, False, False,  True, False,
        True, False, False,  True,  True,  True, False,  True,  True,
        True,  True, False,  True,  True,  True,  True,  True, False,
        True,  True,  True,  True,  True,  True,  True, False,  True,
        True,  True,  True, False,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True, False, False,  True,  True,  True,  True,  True,
       False, False,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True, False,  True,
        True,  True,  True,  True, False,  True,  True,  True, False,
        True,  True,  True,  True,  True, False,  True,  True, False,
       False,  True,  True,  True,  True,  True, False,  True,  True,
        True,  True,  True,  True,  True, False,  True, False, False,
       False,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True, False,  True,  True,  True,  True, False,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True, False,  True,  True,  True,  True, False,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True, False, False,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True])]

    # print(masks)

    for mask in masks:
        df_train = df[mask]
        df_test = df[~mask]
        # print('Training data set length=' + str(len(df_train)))
        # print('Testing data set length=' + str(len(df_test)))

        # expr = """BB_COUNT ~ DAY  + DAY_OF_WEEK + MONTH + HIGH_T + LOW_T + PRECIP"""
        expr = """bugs ~ typedness + commits + sloccount + issuecount"""

        y_train, X_train = dmatrices(expr, df_train, return_type='dataframe')
        y_test, X_test = dmatrices(expr, df_test, return_type='dataframe')

        poisson_training_results = sm.GLM(y_train,
                                          X_train,
                                          family=sm.families.Poisson()).fit()
        # print(poisson_training_results.summary())
        # print(poisson_training_results.mu)
        # print(len(poisson_training_results.mu))

        df_train['BB_LAMBDA'] = poisson_training_results.mu

        df_train['AUX_OLS_DEP'] = df_train.apply(lambda x: (
            (x['bugs'] - x['BB_LAMBDA'])**2 - x['BB_LAMBDA']) / x['BB_LAMBDA'],
                                                 axis=1)

        ols_expr = """AUX_OLS_DEP ~ BB_LAMBDA - 1"""

        aux_olsr_results = smf.ols(ols_expr, df_train).fit()
        # print(aux_olsr_results.params)
        # print(aux_olsr_results.tvalues)

        nb2_training_results = sm.GLM(
            y_train,
            X_train,
            family=sm.families.NegativeBinomial(
                alpha=aux_olsr_results.params[0])).fit()
        print(nb2_training_results.summary())

        nb2_predictions = nb2_training_results.get_prediction(X_test)

        predictions_summary_frame = nb2_predictions.summary_frame()
        # print(predictions_summary_frame)

        # predicted_counts = predictions_summary_frame['mean']
        # actual_counts = y_test['bugs']
        # fig = plt.figure()
        # fig.suptitle('Predicted versus actual bugs')
        # predicted, = plt.plot(X_test.index,
        #                     predicted_counts,
        #                     'go-',
        #                     label='Predicted counts')
        # actual, = plt.plot(X_test.index,
        #                 actual_counts,
        #                 'ro-',
        #                 label='Actual counts')
        # plt.legend(handles=[predicted, actual])
        # plt.show()


if __name__ == "__main__":
    # create_summary_file()
    negative_binomial_regression()
    # print(hmean([0.001, 0.001, 0.071, 0.006, 0.019]))
