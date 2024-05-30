# repository-analysis

## Attributions
All code in  `./papercode` was taken from https://github.com/sola-st/PythonTypeAnnotationStudy
<br>
All code in `harmonic_mean_p.py` was taken from https://github.com/benjaminpatrickevans/harmonicmeanp

## How to reproduce the research performed in the paper
If you want to reproduce the research from scratch, start from step 1. Keep in mind that projects might have evolved since data collection, so results are expected to differ slightly if you start from scratch. If you wish to simply look at the regression results, start from step 8.


1. Create a `.env.local` file containing your GitHub API token in the following format `TOKEN=<your token here>`. A large amount of requests will be made to the GitHub API, so keep this in mind in case you are running other projects using the GitHub API as you will hit the rate-limit at some point.
2. Adjust `PATH_TO_FOLDER_ON_DRIVE` in `settings.py` to point to your preferred folder. Cloned repositories will take up several hundred gigabytes, so make sure you have enough space available.
3. Install all required packages from `requirements.txt`
4. Run `miner.py`. It will mine GitHub for Python repositories. This will take several hours at least. If you hit the rate limit you will have to manually restart the script to continue. Your results might differ from ours due to the internal workings of the GitHub Search API.
5. Run `results.py`. This combines the results from SEART-GHS and our miner.
6. Run `clone.py`. This clones all repositories. Again, your results might differ from ours due to new commits being added since our data collection.
7. Run `metrics.py`. This might take a while. Issue data might differ from ours due to additional issues being closed.
8. Run `regression.py`. It will print descriptive statistics for the dataset and all model results.
9. Edit `harmonic_mean_p.py` to use the p-values you found in the models. Run `harmonic_mean_p.py`
