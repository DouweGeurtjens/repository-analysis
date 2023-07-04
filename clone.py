import json
import os
from pathlib import (Path)

from git import (Repo)
from tqdm import (tqdm)

import settings


def clone_repos():
    with open(settings.ALL_INCLUDED_REPOS_JSON) as f:
        repos = json.load(f)

        for id, repo_name in enumerate(tqdm(repos)):
            print(id)
            path_to_repo = settings.PATH_TO_REPOS.joinpath(str(id))
            # Only clone if not already cloned
            if path_to_repo in settings.PATH_TO_REPOS.iterdir():
                continue

            Repo.clone_from(f"https://github.com/{repo_name}", path_to_repo)


def log_default_branch():
    with open(settings.ALL_INCLUDED_REPOS_JSON) as f:
        repos = json.load(f)
        default_branches = {}
        for id, repo_name in enumerate(tqdm(repos)):
            path_to_repo = settings.PATH_TO_REPOS.joinpath(Path(str(id)))

            # Only analyse if cloned
            if path_to_repo not in settings.PATH_TO_REPOS.iterdir():
                continue

            repo = Repo(path_to_repo)
            default_branches[id] = str(repo.active_branch)

    with open(settings.DEFAULT_BRANCHES_JSON, 'w') as of:
        of.write(json.dumps(default_branches))


clone_repos()
log_default_branch()
