# repository-analysis

This repository is a work in progress.

## Requirements
python
git
git-lfs(?)

# Broken repositories
Some repositories fail during the cloning process for whatever reason. I have yet to resolve these issues, so for now the entries are removed from the `results.json` file and placed into the `removed_results.json` file instead. Below you can find the errors that occured for each broken repository.
<br><br>
```
id: 3984919
name: liberapay/liberapay.com
errog log: 
    git.exc.GitCommandError: Cmd('git') failed due to: exit code(128)
    cmdline: git clone -v -- https://github.com/liberapay/liberapay.com repos/3984919
    stderr: 'Cloning into 'repos/3984919'...
    POST git-upload-pack (175 bytes)
    POST git-upload-pack (gzip 35717 to 18015 bytes)
    Downloading www/assets/fonts/ubuntu-bold-italic-webfont.ttf (357 KB)
    Error downloading object: www/assets/fonts/ubuntu-bold-italic-webfont.ttf (2c33de3): Smudge error: Error downloading www/assets/fonts/ubuntu-bold-italic-webfont.ttf (2c33de34d51065a5e56bae5e1c7c13cd128268b26569838a38db038e6ac9723d): batch request: git@github.com: Permission denied (publickey).: exit status 255

    Errors logged to '***/repos/3984919/.git/lfs/logs/20230325T173444.092742729.log***'.
    Use `git lfs logs last` to view the log.
    error: external filter 'git-lfs filter-process' failed
    fatal: www/assets/fonts/ubuntu-bold-italic-webfont.ttf: smudge filter lfs failed
    warning: Clone succeeded, but checkout failed.
    You can inspect what was checked out with 'git status'
    and retry with 'git restore --source=HEAD :/'
```
