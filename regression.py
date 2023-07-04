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


def get_data_from_files(commit=None):
    # Typedness should be the index I think, not sure
    with open(settings.ALL_INCLUDED_REPOS_JSON) as f:
        repos = json.load(f)
        ids = []
        typedness = []
        bugs = []
        issues = []
        commits = []

        for id, repo_name in enumerate(tqdm(repos)):
            path_to_repo = settings.PATH_TO_REPOS.joinpath(Path(str(id)))
            ar_path = settings.PATH_TO_ANALYSIS_RESULTS.joinpath(str(id))
            is_path = settings.PATH_TO_ISSUES.joinpath(str(id))

            # Only do the rest if both folders exist
            if ar_path not in settings.PATH_TO_ANALYSIS_RESULTS.iterdir():
                continue
            if is_path not in settings.PATH_TO_ISSUES.iterdir():
                continue

            ars = list(ar_path.iterdir())
            iss = list(is_path.iterdir())

            # Checkout the default branch in case we're not on it for some reason
            repo = Repo(path_to_repo)
            # try:
            #     repo.git.checkout(repo_default_branch)
            # except:
            #     print(f"Failed on repo with id: {id}")
            #     continue

            # Checkout relevant commit if supplied, else checkout latest
            if commit:
                pass
            else:
                checked_out_commit = next(repo.iter_commits())
                repo.git.checkout(checked_out_commit)

            total_commits_for_repo = 0
            for i in repo.iter_commits():
                total_commits_for_repo += 1

            with open(
                    ar_path.joinpath(
                        Path(f'typedness_{checked_out_commit}.json'))) as arsf:
                ob = json.load(arsf)
                obb = ob['total']
                total = obb["number_param_types"] + obb[
                    "number_return_types"] + obb["number_variable_types"] + obb[
                        "number_non_param_types"] + obb[
                            "number_non_return_types"] + obb[
                                "number_non_variable_types"]
                typed = obb["number_param_types"] + obb[
                    "number_return_types"] + obb["number_variable_types"]
                if total != 0:
                    typedness_for_repo = (int(typed) / int(total)) * 100
                else:
                    typedness_for_repo = 0

            with open(is_path.joinpath(Path('issues.json'))) as iss:
                iss_data = json.load(iss)
                bugs_for_repo = len(iss_data)

            ids.append(id)
            typedness.append(typedness_for_repo)
            bugs.append(bugs_for_repo)
            commits.append(total_commits_for_repo)
    ret = {
        'typedness': typedness,
        'repo': ids,
        'bugs': bugs,
        'commits': commits,
        # 'issuecount': [1, 2]
    }
    with open('./testt.json', 'w') as ff:
        j = json.dumps(ret, indent=4)
        ff.write(j)

    return ret


def negative_binomial_regression():
    # https://timeseriesreasoning.com/contents/negative-binomial-regression-model/
    # data = get_data_from_files()
    data = {}
    with open('./testt.json') as f:
        j = json.load(f)
        data['typedness'] = j['typedness']
        data['bugs'] = j['bugs']
        data['commits'] = j['commits']
    df = pd.DataFrame(data=data)
    print(df)
    df = df[~((df['bugs'] == 0) | (df['bugs'] == 2))]
    print(df)
    mask = np.random.rand(len(df)) < 0.8
    df_train = df[mask]
    df_test = df[~mask]
    print('Training data set length=' + str(len(df_train)))
    print('Testing data set length=' + str(len(df_test)))

    # expr = """BB_COUNT ~ DAY  + DAY_OF_WEEK + MONTH + HIGH_T + LOW_T + PRECIP"""
    expr = """bugs ~ typedness + commits"""

    y_train, X_train = dmatrices(expr, df_train, return_type='dataframe')
    y_test, X_test = dmatrices(expr, df_test, return_type='dataframe')

    poisson_training_results = sm.GLM(y_train,
                                      X_train,
                                      family=sm.families.Poisson()).fit()
    print(poisson_training_results.summary())
    print(poisson_training_results.mu)
    print(len(poisson_training_results.mu))

    df_train['BB_LAMBDA'] = poisson_training_results.mu

    df_train['AUX_OLS_DEP'] = df_train.apply(lambda x: (
        (x['bugs'] - x['BB_LAMBDA'])**2 - x['BB_LAMBDA']) / x['BB_LAMBDA'],
                                             axis=1)

    ols_expr = """AUX_OLS_DEP ~ BB_LAMBDA - 1"""

    aux_olsr_results = smf.ols(ols_expr, df_train).fit()
    print(aux_olsr_results.params)
    print(aux_olsr_results.tvalues)

    nb2_training_results = sm.GLM(y_train,
                                  X_train,
                                  family=sm.families.NegativeBinomial(
                                      alpha=aux_olsr_results.params[0])).fit()
    print(nb2_training_results.summary())

    nb2_predictions = nb2_training_results.get_prediction(X_test)

    predictions_summary_frame = nb2_predictions.summary_frame()
    print(predictions_summary_frame)

    predicted_counts = predictions_summary_frame['mean']
    actual_counts = y_test['bugs']
    fig = plt.figure()
    fig.suptitle('Predicted versus actual bugs')
    predicted, = plt.plot(X_test.index,
                          predicted_counts,
                          'go-',
                          label='Predicted counts')
    actual, = plt.plot(X_test.index,
                       actual_counts,
                       'ro-',
                       label='Actual counts')
    plt.legend(handles=[predicted, actual])
    plt.show()


negative_binomial_regression()