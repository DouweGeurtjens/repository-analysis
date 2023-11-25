import os
from pathlib import (Path)
from dotenv import load_dotenv

load_dotenv('.env.local')

TOKEN = os.getenv('TOKEN')
ALL_INCLUDED_REPOS_JSON = Path('./all_included_repos.json')
DEFAULT_BRANCHES_JSON = Path('./default_branches.json')
PATH_TO_FOLDER_ON_DRIVE = Path('/media/douwe/Elements/HONORS')
PATH_TO_REPOS = PATH_TO_FOLDER_ON_DRIVE.joinpath(Path('repos'))
PATH_TO_ANALYSIS_RESULTS = PATH_TO_FOLDER_ON_DRIVE.joinpath(Path('results'))
PATH_TO_ISSUES = PATH_TO_FOLDER_ON_DRIVE.joinpath(Path('issues'))
