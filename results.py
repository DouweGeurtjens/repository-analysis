import json


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
    with open('all_included_repos.json', 'w') as f3:
        print(len(union))
        f3.write(json.dumps(list(union)))


if __name__ == '__main__':
    results_union()