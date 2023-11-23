import json
from pathlib import (Path)

from git import (Repo)
from tqdm import (tqdm)
import requests

import settings


def get_bug_issues() -> None:
    magic_map = {
        "noqqe/entbehrlich.es":
        "NULL",
        "numpy/numpy":
        "00 - Bug",
        "lmfdb/lmfdb":
        "production issue",
        "cupy/cupy":
        "cat:bug",
        "OpenNMT/OpenNMT-py":
        "type:bug",
        "the-tale/the-tale":
        "type_bug",
        "SickChill/sickchill":
        "Bug / Issue",
        "forseti-security/forseti-security":
        "type: bug",
        "epiphany-platform/epiphany":
        "type/bug",
        "inspirehep/inspire-next":
        "Type: Bug",
        "mailpile/Mailpile":
        "Bugs",
        "python-discord/bot":
        "t: bug",
        "TebbaaX/DownTime-Score":
        "NULL",
        "SciTools/iris":
        "Type: Bug",
        "endpointcorp/end-point-blog":
        "bug",
        "ewels/multiqc": ["core: bug", "module: bug"],
        "emissary-ingress/emissary":
        "t:bug",
        "ninja-ide/ninja-ide":
        "type: bug",
        "kserve/kserve":
        "kind/bug",
        "statsmodels/statsmodels": ["type-bug", "type-bug-wrong"],
        "kubernetes-client/python":
        "kind/bug",
        "googlefonts/noto-fonts":
        "NULL",
        "threefoldtech/js-sdk":
        "type_bug",
        "feast-dev/feast":
        "kind/bug",
        "numenta/nupic":
        "type:bug",
        "nautobot/nautobot":
        "type: bug",
        "dmlc/dgl":
        "bug:confirmed",
        "openNAMU/openNAMU":
        "A 버그 (Bug)",
        "scikit-image/scikit-image":
        ":bug: Bug",
        "networkx/networkx":
        "type: Bug fix",
        "zimmerman-team/iati.cloud":
        "BUG / FIX ME / HELP WANTED",
        "scipy/scipy":
        "defect",
        "mpmg-dcc-ufmg/c01":
        "[1] Bug",
        "quantumlib/cirq":
        "kind/bug-report",
        "cernanalysispreservation/analysispreservation.cern.ch":
        "Type: bug",
        "fedora-infra/bodhi":
        "bugzilla",
        "opennamu/opennamu":
        "A 버그 (Bug)",
        "mozilla/experimenter":
        "Defect",
        "apache/tvm":
        "type: bug",
        "cocotb/cocotb":
        "type:bug",
        "tautulli/tautulli":
        "type:bug",
        "easybuilders/easybuild-easyconfigs":
        "bug report",
        "PyCQA/flake8":
        "bug:confirmed",
        "qutebrowser/qutebrowser":
        ["bug: behavior", "bug: exception", "bug: segfault/crash/hang"],
        "kivymd/kivymd":
        "Type: Bug",
        "nodejs/node-gyp":
        "Confirmed-bug",
        "MPMG-DCC-UFMG/C01":
        "[1] Bug",
        "SwissDataScienceCenter/renku-python":
        "kind/bug",
        "cernopendata/opendata.cern.ch":
        "Type: bug",
        "python-telegram-bot/python-telegram-bot":
        "bug :bug:",
        "celery/celery":
        "Issue Type: Bug Report",
        "opennmt/opennmt-py":
        "type:bug",
        "d2l-ai/d2l-vi":
        "type: bug",
        "pypa/pip":
        "type: bug",
        "learning-unlimited/ESP-Website":
        "Error",
        "isocpp/cppcoreguidelines":
        "NULL",
        "HibiKier/zhenxun_bot":
        "bug",
        "nginx-proxy/nginx-proxy":
        "kind/bug",
        "hyperspy/hyperspy":
        "type: bug",
        "exercism/python":
        "bug 🐛",
        "HyphaApp/hypha":
        "Type: Bug",
        "Ericsson/codechecker":
        "bug :bug:",
        "aws/aws-sam-cli":
        "type/bug",
        "hyphaapp/hypha":
        "Type: Bug",
        "openshift/openshift-ansible":
        "kind/bug",
        "mozilla/addons-server":
        "type:bug",
        "aiidateam/aiida-core":
        "type/bug",
        "globaleaks/globaleaks":
        "T: Bug",
        "TheLastBen/fast-stable-diffusion":
        "bug",
        "OpenMined/PySyft":
        "Type: Bug :bug:",
        "Just-Some-Bots/MusicBot":
        "t/bug",
        "pycqa/flake8":
        "bug:confirmed",
        "dmwm/CRABServer":
        "Type: Bug",
        "unidata/metpy":
        "Type: Bug",
        "tensorflow/models":
        "type:bug",
        "ESMCI/cime":
        "ty: Bug",
        "mars-project/mars":
        "type: bug",
        "pennersr/django-allauth":
        "FIXME",
        "canonical/microk8s":
        "kind/bug",
        "rootzoll/raspiblitz":
        "bug - confirmed",
        "python-poetry/poetry":
        "kind/bug",
        "Tribler/tribler":
        "type: bug",
        "ReactionMechanismGenerator/RMG-Py":
        "Type: Bug",
        "privacyidea/privacyidea":
        "Type: Bug",
        "frescobaldi/frescobaldi":
        "defect",
        "sphinx-doc/sphinx":
        "type:bug",
        "UKPLab/sentence-transformers":
        "bug",
        "lbryio/lbry-sdk":
        "type: bug",
        "netbox-community/netbox":
        "type: bug",
        "django-cms/django-cms":
        "kind: bug",
        "holoviz/panel":
        "type: bug",
        "conda/conda-build":
        "type::bug",
        "kivy/kivy":
        "Type: Bug",
        "EndPointCorp/end-point-blog":
        "bug",
        "globaleaks/GlobaLeaks":
        "T: Bug",
        "electricitymaps/electricitymaps-contrib":
        "bug 🐞",
        "ansible/galaxy":
        "type/bug",
        "powerline/powerline":
        "t:bug",
        "nortikin/sverchok":
        "bug :bug:",
        "argilla-io/argilla":
        "bug 🪲",
        "airbytehq/airbyte":
        "type/bug",
        "internetarchive/openlibrary":
        "Type: Bug",
        "TIM-JYU/TIM":
        "bugi",
        "carpentries/amy":
        "type: bug",
        "dmwm/crabserver":
        "Type: Bug",
        "bokeh/bokeh":
        "type: bug",
        "benoitc/gunicorn":
        "- Bugs -",
        "frida/frida":
        "bug",
        "DemocracyClub/UK-Polling-Stations":
        "bug :bug:",
        "snarfed/bridgy":
        "NULL",
        "esmci/cime":
        "ty: Bug",
        "pywbem/pywbem":
        "type: bug",
        "zestedesavoir/zds-site":
        "S-BUG",
        "thoth-station/solver":
        "kind/bug",
        "coala/coala-bears":
        "type/bug",
        "streamlit/streamlit":
        "type:bug",
        "spesmilo/electrum":
        "bug 🐞",
        "iperov/deepfacelab":
        "bug",
        "cloud-custodian/cloud-custodian":
        "kind/bug",
        "aws/serverless-application-model":
        "type/bug",
        "guake/guake":
        "Type: Defect",
        "datadog/dd-agent":
        "bugfix",
        "kubeflow/pipelines":
        "kind/bug",
        "sickchill/sickchill":
        "Bug / Issue",
        "democracyclub/uk-polling-stations":
        "bug :bug:",
        "Tautulli/Tautulli":
        "type:bug",
        "tencent/bk-sops":
        "type/bug",
        "bsdata/warhammer-age-of-sigmar":
        "Type: bug",
        "jina-ai/jina":
        "type/bug",
        "spyder-ide/spyder":
        "type:Bug",
        "sosreport/sos":
        "NULL",
        "isocpp/CppCoreGuidelines":
        "NULL",
        "tornadoweb/tornado":
        "NULL",
        "scverse/scanpy":
        "Bug 🐛",
        "Scifabric/pybossa":
        "NULL",
        "ManimCommunity/manim":
        "issue:bug",
        "elyra-ai/elyra":
        "kind:bug",
        "iperov/DeepFaceLab":
        "bug",
        "plone/products.cmfplone":
        "01 type: bug",
        "ansible/awx":
        "type:bug",
        "scitools/cartopy":
        "Type: Bug",
        "datalad/datalad":
        "NULL",
        "PennyDreadfulMTG/Penny-Dreadful-Tools":
        "+ bug",
        "obi-ontology/obi":
        "NULL",
        "getsentry/sentry":
        "Type: Bug",
        "pypi/warehouse":
        "bug :bug:",
        "ericsson/codechecker":
        "bug :bug:",
        "keras-team/keras":
        "type:Bug",
        "django-oscar/django-oscar":
        "☁ Bug",
        "radical-cybertools/radical.pilot":
        "type:bug",
        "RasaHQ/rasa":
        "type:bug :bug:",
        "MIC-DKFZ/nnUNet":
        "bug :bug:",
        "XX-net/XX-Net":
        "分类_bug",
        "camptocamp/c2cgeoportal":
        "bug",
        "mdn/kuma":
        "type: bug report",
        "xx-net/xx-net":
        "分类_bug",
        "meltano/meltano":
        "kind/Bug",
        "psychopy/psychopy":
        "🐞 bug",
        "rasahq/rasa":
        "type:bug :bug:",
        "plone/Products.CMFPlone":
        "01 type: bug",
        "DataDog/dd-agent":
        "bugfix",
        "pennydreadfulmtg/penny-dreadful-tools":
        "+ bug",
        "scifabric/pybossa":
        "NULL",
        "conda/conda":
        "type::bug",
        "pyca/cryptography":
        "bugs",
        "modin-project/modin":
        "bug 🦗",
        "webcompat/webcompat.com":
        "type: bug",
        "pypa/pipenv":
        "Type: Bug :bug:",
        "googlecloudplatform/python-docs-samples":
        "type: bug",
        "realfagstermer/realfagstermer":
        "feil",
        "realodix/adblockid":
        "C: Bug",
        "pypa/warehouse":
        "bug :bug:",
        "sagemath/sage":
        "t: bug",
        "mailu/mailu":
        "type/bug",
        "vispy/vispy":
        "type: bug",
        "ynput/OpenPype":
        "type: bug",
        "jumpserver/jumpserver":
        "类型:Bug",
        "manimcommunity/manim":
        "issue:bug",
        "coreruleset/coreruleset":
        ":bug: bug",
        "pylint-dev/pylint":
        "Bug :beetle:",
        "unifyai/ivy":
        "Bug Report",
        "tribler/tribler":
        "type: bug",
        "LmeSzinc/AzurLaneAutoScript":
        "bug / 缺陷",
        "Pylons/pyramid":
        "bugs",
        "python/cpython":
        "type-bug",
        "psf/black":
        "T: bug",
        "mdanalysis/mdanalysis":
        "defect",
        "WordPress/openverse":
        "🛠 goal: fix",
        "kedro-org/kedro":
        "Issue: Bug Report 🐞",
        "matrix-org/synapse": ["T-Defect", "z-bug"],
        "googlefonts/fontbakery":
        "Tool bug",
        "matplotlib/matplotlib":
        "PR: bugfix",
        "SirVer/ultisnips": ["bug: low", "bug: medium", "bug: severe"],
        "marcizhu/marcizhu":
        "NULL",
        "scitools/iris":
        "Type: Bug",
        "swissdatasciencecenter/renku-python":
        "kind/bug",
        "easybuilders/easybuild-framework":
        "bug report",
        "liqd/a4-meinberlin":
        "Type: Bug",
        "raiden-network/raiden":
        "Type / Bug",
        "Ultimaker/Cura":
        "Type: Bug",
        "centerofci/mathesar":
        "type: bug",
        "openshot/openshot-qt":
        ":lady_beetle: bug",
        "islandora/documentation":
        "Type: bug",
        "chainer/chainer":
        "cat:bug",
        "Unidata/MetPy":
        "Type: Bug",
        "pylons/pyramid":
        "bugs",
        "komodo/komodoedit":
        "Type: Bug",
        "onaio/onadata":
        "Error",
        "gevent/gevent":
        "Type: Bug",
        "ultimaker/cura":
        "Type: Bug",
        "OpenShot/openshot-qt":
        ":lady_beetle: bug",
        "googleapis/google-cloud-python":
        "type: bug",
        "urllib3/urllib3":
        "NULL",
        "Cog-Creators/Red-DiscordBot":
        "Type: Bug",
        "ukplab/sentence-transformers":
        "bug",
        "wazuh/wazuh-qa":
        "type/bug",
        "httpwg/http-extensions":
        "NULL",
        "SciTools/cartopy":
        "Type: Bug",
        "sirver/ultisnips":
        "bug: low, bug: medium. bug: severe",
        "holoviz/holoviews":
        "type: bug",
        "nlplab/brat":
        "type-bug",
        "quantumlib/Cirq":
        "kind/bug-report",
        "Islandora/documentation":
        "Type: bug",
        "TencentBlueKing/bk-sops":
        "type/bug",
        "mopidy/mopidy":
        "C-bug",
        "reactionmechanismgenerator/rmg-py":
        "Type: Bug",
        "pupil-labs/pupil":
        "type: bug",
        "sasview/sasview":
        "Defect",
        "coala/coala":
        "type/bug",
        "ewels/MultiQC": ["core: bug", "module: bug"],
        "Supervisor/supervisor":
        "NULL",
        "galaxyproject/galaxy":
        "kind/bug",
        "Komodo/KomodoEdit":
        "Type: Bug",
        "docker/docker-py":
        "kind/bug",
        "learning-unlimited/esp-website":
        "Error",
        "hacs/integration":
        "pr: bugfix",
        "pytest-dev/pytest":
        "type: bug",
        "wagtail/wagtail":
        "type:Bug",
        "heartexlabs/label-studio":
        "NULL",
        "LMFDB/lmfdb":
        "production issue",
        "python/typeshed":
        "NULL",
        "M157q/m157q.github.io":
        "NULL",
        "electricitymap/electricitymap-contrib":
        "bug 🐞",
        "sonic-net/sonic-mgmt":
        "Bug :bug:",
        "BSData/warhammer-age-of-sigmar":
        "Type: bug",
        "openstates/openstates-scrapers":
        "NULL",
        "bikalims/bika.lims":
        "type: bug",
        "pygments/pygments":
        "T-bug",
        "SasView/sasview":
        "Defect",
        "nucypher/nucypher":
        "Bug :bug:",
        "Mailu/Mailu":
        "type/bug",
        "cobbler/cobbler":
        "Bug Report",
        "zimmerman-team/IATI.cloud":
        "BUG / FIX ME / HELP WANTED",
        "MDAnalysis/mdanalysis":
        "defect",
        "ballerina-platform/ballerina-standard-library":
        "Type/Bug",
        "deepset-ai/haystack":
        "type:bug",
        "m-labs/artiq":
        "type:bug",
        "mitmproxy/mitmproxy":
        "kind/bug",
        "Guake/guake":
        "Type: Defect",
        "mailpile/mailpile":
        "Bugs",
        "supervisor/supervisor":
        "NULL",
        "apache/airflow":
        "kind:bug",
        "kivymd/KivyMD":
        "Type: Bug",
        "cython/cython":
        "defect",
        "cog-creators/red-discordbot":
        "Type: Bug",
        "open-mmlab/mmpose":
        "kind/bug",
        "localstack/localstack":
        "type: bug",
    }
    with open(settings.ALL_INCLUDED_REPOS_JSON) as f:
        repos = json.load(f)

        for id, repo_name in enumerate(tqdm(repos)):
            if repo_name in magic_map:
                path_to_repo_issues = settings.PATH_TO_ISSUES.joinpath(str(id))
                print(repo_name)
                # Only get bugs if not already collected
                # if path_to_repo_issues in settings.PATH_TO_ISSUES.iterdir():
                #     continue

                headers = {'Authorization': f'token {settings.TOKEN}'}

                bugs = []
                if isinstance(magic_map[repo_name], str):
                    l = [magic_map[repo_name]]
                else:
                    l = magic_map[repo_name]

                for label in l:
                    payload = {'state': 'closed', 'labels': l}
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

                print(f"Found {len(bugs)} number of bugs!")
                # Make the directory only before we write to the file
                path_to_repo_issues.mkdir(exist_ok=True, parents=True)
                # Write the entire JSON response to a file so we don't have to repull stuff from GitHub constantly
                with open(path_to_repo_issues.joinpath('issues.json'),
                          'w') as of:
                    j = json.dumps(bugs, indent=4)
                    of.write(j)


if __name__ == "__main__":
    get_bug_issues()