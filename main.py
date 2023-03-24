from git import (Repo)
from tqdm import (tqdm)


def main():
    # General outline
    #   Clone repos according to results from https://seart-ghs.si.usi.ch/
    #   For each repo, use GitHub API to find several commit hashes based on their relative commit number
    #   Use GitPython to checkout each commit and run some analysis on the typedness of a repository
    #   Try to make an initial classification of the type of repository (typehinting vs no typehinting)    #
    #   Evidently, this naive method of classification is not exhaustive but serves as a rough initial outline
    pass


main()