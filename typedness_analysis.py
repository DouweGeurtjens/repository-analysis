import json
import os
from pathlib import (Path)
from tqdm import (tqdm)
from pydriller import Repository, Git
from git import Repo

import settings
from papercode.TypeErrors.TypeAnnotationCounter import count_type_annotations


def paper_typedness_analysis(commit=None):
    with open(settings.ALL_INCLUDED_REPOS_JSON) as f:
        repos = json.load(f)

        for id, repo_name in enumerate(tqdm(repos)):

            # Bricks on these repos: 352, 374, 437, 491, 541, 550, 580, 591, 593, 632
            if id in [352, 374, 437, 491, 541, 550, 580, 591, 593, 632]:
                continue

            path_to_repo = settings.PATH_TO_REPOS.joinpath(Path(str(id)))
            path_to_analysis_results_dir_for_repo = settings.PATH_TO_ANALYSIS_RESULTS.joinpath(
                Path(str(id)))

            # Only analyse if cloned
            if path_to_repo not in settings.PATH_TO_REPOS.iterdir():
                continue

            # Only analyse if not already analysed
            if path_to_analysis_results_dir_for_repo in settings.PATH_TO_ANALYSIS_RESULTS.iterdir(
            ):
                continue

            # Get the default branch for this repo
            repo_default_branch = None
            with open(settings.DEFAULT_BRANCHES_JSON, 'r') as dbf:
                default_branches = json.load(dbf)
                repo_default_branch = default_branches[str(id)]

            # Checkout the default branch in case we're not on it for some reason
            repo = Repo(path_to_repo)
            try:
                repo.git.checkout(repo_default_branch)
            except:
                print(f"Failed on repo with id: {id}")
                continue

            # Checkout relevant commit if supplied, else checkout latest
            if commit:
                pass
            else:
                checked_out_commit = next(repo.iter_commits())
                repo.git.checkout(checked_out_commit)

            # Set the path for the output file using the checked_out_commit so we can distinguish between results at different points in time
            path_to_analysis_results_file_for_repo = path_to_analysis_results_dir_for_repo.joinpath(
                Path(f'typedness_{checked_out_commit}.json'))

            # Only analyse if not already analysed
            # First check if the folder for the analysed repo exists in the first place, only then check for the file
            if path_to_analysis_results_dir_for_repo in settings.PATH_TO_ANALYSIS_RESULTS.iterdir(
            ):
                if path_to_analysis_results_file_for_repo in path_to_analysis_results_dir_for_repo.iterdir(
                ):
                    continue

            res = count_type_annotations(
                settings.PATH_TO_REPOS.joinpath(Path(str(id))))

            dump = json.dumps(res, indent=4).encode()

            output_file = path_to_analysis_results_file_for_repo
            output_file.parent.mkdir(exist_ok=True, parents=True)
            output_file.write_bytes(dump)


paper_typedness_analysis()