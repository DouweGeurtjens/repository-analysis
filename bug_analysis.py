import json
from pathlib import (Path)

from git import (Repo)
from tqdm import (tqdm)
import requests

import settings


def get_bug_issues() -> None:
    with open(settings.ALL_INCLUDED_REPOS_JSON) as f:
        repos = json.load(f)

        for id, repo_name in enumerate(tqdm(repos)):
            path_to_repo_issues = settings.PATH_TO_ISSUES.joinpath(str(id))

            # Only get bugs if not already collected
            if path_to_repo_issues in settings.PATH_TO_ISSUES.iterdir():
                continue

            headers = {'Authorization': f'token {settings.TOKEN}'}
            payload = {'state': 'closed', 'labels': 'bug'}
            bugs = []

            r = requests.get(
                f"https://api.github.com/repos/{repo_name}/issues",
                params=payload,
                headers=headers)
            if r.status_code != 200:
                print(f'Failed on id: {id}')
                print(r.text)
                raise Exception
            bugs.extend(r.json())

            while 'next' in r.links:
                next_url = r.links['next']['url']
                r = requests.get(next_url, headers=headers)
                bugs.extend(r.json())

            # Make the directory only before we write to the file
            path_to_repo_issues.mkdir(exist_ok=True, parents=True)
            # Write the entire JSON response to a file so we don't have to repull stuff from GitHub constantly
            with open(path_to_repo_issues.joinpath('issues.json'), 'w') as of:
                j = json.dumps(bugs, indent=4)
                of.write(j)


get_bug_issues()