import datetime
import json
from pathlib import Path
import os

from dotenv import load_dotenv
import requests

CURRENT_DIRECTORY = os.path.dirname(__file__)

load_dotenv(os.path.join(CURRENT_DIRECTORY, '../.env.local'))
TOKEN = os.getenv('TOKEN')


def create_date_range_tracker():
    daterange_tracker = os.path.join(CURRENT_DIRECTORY, './daterange.tracker')
    with open(daterange_tracker, 'w') as f:
        end = datetime.datetime.today()
        start = datetime.datetime.today() - datetime.timedelta(days=1)
        f.writelines(
            f"{start.strftime('%Y-%m-%d')}..{end.strftime('%Y-%m-%d')}\n")
        while start >= datetime.datetime.strptime('2008-02-10', '%Y-%m-%d'):
            end = start - datetime.timedelta(days=1)
            start = end - datetime.timedelta(days=1)
            f.writelines(
                f"{start.strftime('%Y-%m-%d')}..{end.strftime('%Y-%m-%d')}\n")


def get_github_repos():
    daterange_tracker = os.path.join(CURRENT_DIRECTORY, './daterange.tracker')
    with open(daterange_tracker, 'r+') as f:
        lines = f.readlines()

        # We can't pop from the list otherwise
        for daterange in list(lines):

            has_next_page = True
            current_pagination_id = ""
            # Query parameter that determines the daterange in which a repository was created
            # Used to get around the 1000 result limit per query by narrowing the search range
            created = f'created:{daterange.strip()}'
            print(f"Getting repos for daterange {daterange.strip()}...")
            while has_next_page:
                print(current_pagination_id)
                # Only specify the "after" key in the query if we have a pagination id
                after = f', after: "{current_pagination_id}"' if current_pagination_id else ""

                # Query with dynamically inserted pagination id and creation dates
                query = f"""
                    query MyQuery {{
                        search(query: "language:python {created}", type: REPOSITORY, first: 100{after}) {{
                            edges {{
                                node {{
                                    ... on Repository {{
                                        id
                                        name
                                        nameWithOwner
                                        issues {{
                                            totalCount
                                        }}
                                        isFork
                                        pushedAt
                                        defaultBranchRef {{
                                            target {{
                                                ... on Commit {{
                                                    history {{
                                                        totalCount
                                                    }}
                                                }}
                                            }}
                                        }}
                                    }}
                                }}
                            }}
                            pageInfo {{
                                endCursor
                                startCursor
                                hasNextPage
                                hasPreviousPage
                            }}
                        }}
                        rateLimit {{
                            remaining
                        }}
                    }}
                """

                headers = {'Authorization': f'token {TOKEN}'}
                payload = {'query': query}
                r = requests.post(f"https://api.github.com/graphql",
                                  json=payload,
                                  headers=headers)

                if r.status_code != 200:
                    f.seek(0)
                    f.truncate()
                    f.writelines(lines)
                    raise Exception(
                        f"Received a {r.status_code} response code with body\n {r.json()}"
                    )

                query_result = r.json()
                # Write the entire JSON response to a file so we don't have to repull stuff from GitHub constantly
                with open(
                        os.path.join(
                            CURRENT_DIRECTORY,
                            f'./query-results/res_{created}_{query_result["data"]["search"]["pageInfo"]["startCursor"]}.json'
                        ), 'w') as res_f:
                    j = json.dumps(query_result)
                    res_f.write(j)

                # If there is a next page we update the current_pagination_id
                # Otherwise we're done so we set our loop condition to false
                if query_result["data"]["search"]["pageInfo"]["hasNextPage"]:
                    current_pagination_id = query_result["data"]["search"][
                        "pageInfo"]["endCursor"]
                else:
                    has_next_page = False

                # If we hit the rate limit we write the modified daterange.tracker lines and exit
                if query_result["data"]["rateLimit"]["remaining"] == 0:
                    print("Hit rate limit, updating daterange.tracker")
                    f.seek(0)
                    f.truncate()
                    f.writelines(lines)
                    return

            try:
                lines.pop(0)
            except IndexError:
                print('Reached end of daterange, finished mining')
        f.seek(0)
        f.truncate()
        f.writelines(lines)


def filter_repos():
    filtered_results = []
    total_repos = 0
    added_repos = 0
    query_results = os.listdir(
        os.path.join(CURRENT_DIRECTORY, './query-results'))

    for file_name in query_results:
        with open(
                os.path.join(CURRENT_DIRECTORY,
                             f'./query-results/{file_name}')) as f:
            query_result = json.load(f)

            for repo in query_result['data']['search']['edges']:
                total_repos = total_repos + 1
                if repo['node']['issues']['totalCount'] < 1000:
                    continue
                if repo['node']['isFork']:
                    continue
                if datetime.datetime.strptime(
                        repo['node']['pushedAt'],
                        '%Y-%m-%dT%H:%M:%SZ') < datetime.datetime.strptime(
                            '2022-03-31T12:00:00', '%Y-%m-%dT%H:%M:%S'):
                    continue
                if repo['node']['defaultBranchRef']['target']['history'][
                        'totalCount'] < 1000:
                    continue

                filtered_results.append(repo['node']['nameWithOwner'])
                added_repos = added_repos + 1

    with open(os.path.join(CURRENT_DIRECTORY, './filtered-results/res.json'),
              'w') as res_f:
        j = json.dumps(filtered_results)
        res_f.write(j)

    print(
        f'Checked {total_repos} repositories of which {added_repos} met the criteria for a ratio of {(added_repos/total_repos) * 100} precent'
    )


# create_date_range_tracker()
# get_github_repos()
filter_repos()