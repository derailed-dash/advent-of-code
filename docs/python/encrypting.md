---
title: Encrypting Your Input
description: How to keep Advent of Code puzzle inputs and private repository secrets secure and compliant using git-crypt, parallel .enc files, and git-crypt-helper.sh.
main_img:
  name: Jupyter Notebook
  link: /assets/images/encrypting.jpg
tags: 
  - name: No Aggregating inputs
    link: https://www.reddit.com/r/adventofcode/wiki/faqs/copyright/inputs/
  - name: git-crypt
    link: https://github.com/AGWA/git-crypt
---
## Page Contents

- [Don't Share Your Input Data](#dont-share-your-input-data)
- [What To Do?](#what-to-do)
- [How to Encrypt?](#how-to-encrypt)
- [Working with Git-Crypt](#working-with-git-crypt)
  - [Installation](#installation)
  - [Per-Repo (or Across Repos) Setup](#per-repo-or-across-repos-setup)
  - [Using Git-Crypt in Your Repo](#using-git-crypt-in-your-repo)
  - [Parallel Encrypted Files (.enc Pattern)](#parallel-encrypted-files-enc-pattern)
  - [Automating Secrets with git-crypt-helper.sh](#automating-secrets-with-git-crypt-helpersh)
  - [Detecting Locked Blobs and Cleaning Inputs](#detecting-locked-blobs-and-cleaning-inputs)
  - [Useful Git-Crypt Commands](#useful-git-crypt-commands)
  - [Cloning an Existing Repo with Encrypted Files](#cloning-an-existing-repo-with-encrypted-files)
  - [Retrospective Encryption](#retrospective-encryption)
  - [What Does It Look Like in GitHub?](#what-does-it-look-like-in-github)
  - [Troubleshooting](#troubleshooting)

## Don't Share Your Input Data

Input data is unique to users. The input data that I am assigned (for any given AoC puzzle) will be different to the input data that you see.

Eric, the creator of Advent of Code, has requested that participants do not share their input data. As described [here](https://www.reddit.com/r/adventofcode/wiki/faqs/copyright/inputs/){:target="_blank"}, sharing the input files would make it easier for someone to steal the entire AoC site. AoC is an immensely valuable and useful creation, and we don't want to help any freeloaders to steal the intellectual property into which Eric has put so much time and effort.

## What To Do?

Personally, I always want to be able to store my input data, along with my solution. That way, I can synchronise my repo across multiple devices, and be sure I'm always working with the same input data.

Furthermore, I want to share my solutions with all of you. And as such, my [repo](https://github.com/derailed-dash/Advent-of-Code){:target="_blank"} is public. But I don't want to share my input data with anyone else.

My solution: **encrypt the input data.**

## How to Encrypt?

There are many ways to encrypt data that you check in to GitHub. But one method I like is [git-crypt](https://github.com/AGWA/git-crypt){:target="_blank"}. Git-Crypt performs **transparent encryption and decryption** of selected files, when pushing to or pulling from your GitHub repo. Thus, once you've set it up, you don't need to do anything. It just works.

## Working with Git-Crypt

### Installation

First, you'll need to install Git-Crypt. On Linux (or Linux on Windows using WSL2, which is the recommended development setup):

```bash
sudo apt install git-crypt
```

On macOS, you can install it via Homebrew:

```bash
brew install git-crypt
```

If you are developing on Windows, I strongly recommend working inside WSL2 (Ubuntu/Debian) and installing `git-crypt` via `apt` as shown above. Running Git commands directly inside WSL ensures that all Git hooks, smudge/clean filters, and helper scripts operate consistently in the native Linux environment without path or line-ending mismatches.

### Per-Repo (or Across Repos) Setup

Now you need to create a key, which you must store securely. You can do this *per repo*, but you can also use the same shared key between multiple repos. (If you've already got a key, be careful not to overwrite it!)

```bash
git-crypt init # generate the secure key
git-crypt export-key ../git-crypt-key # exports the symmetric key
```

Now **store the symmetric key securely**! If you need to decrypt your repo on another machine, you'll need to supply this key. For example, you could store the key in a password manager.

> [!CAUTION]
> **Never run `git-crypt init` on a cloned repository that already contains encrypted files!**
> Running `git-crypt init` generates a *brand new, incompatible key* that will break your local working copy and make it impossible to unlock existing encrypted files. When cloning an existing repository, always use `git-crypt unlock <path-to-key>` instead.

### Using Git-Crypt in Your Repo

Create a `.gitattributes` file in the root of your repo (alongside your `.gitignore` file). This file tells Git which files need to be automatically encrypted and decrypted with `git-crypt`.

For example, if all your puzzle input files match `input*.txt`:

```text
input*.txt filter=git-crypt diff=git-crypt
```

Now commit your `.gitattributes`.

### Parallel Encrypted Files (.enc Pattern)

Some files need to be untracked in plaintext — such as local `.env` files with secret API tokens, `docs/.env`, or agent skill definitions that external tools might rewrite outside Git. For these, we track a **parallel `.enc` twin** instead:

1. Ignore the plaintext file in `.gitignore` (e.g. `.env`, `docs/.env`, `/.agents/skills/*/SKILL.md`).
2. Encrypt `*.enc` in `.gitattributes`:
   ```text
   *.enc filter=git-crypt diff=git-crypt
   ```
3. Commit a companion template (e.g. `.env.template` and `docs/.env.template`) documenting expected variable keys without real secrets.

### Automating Secrets with git-crypt-helper.sh

To keep plaintext secrets and their encrypted `.enc` twins synchronised without manual copy-paste errors, we use `git-crypt-helper.sh` from `PATH` (wrapped in this repository by `make sync-secrets`):

```bash
# Check encryption state and sync status across all parallel .enc files
git-crypt-helper.sh status      # or: make sync-secrets

# Restore plaintext files from their .enc twins (e.g. after a fresh clone)
git-crypt-helper.sh sync-from-enc

# Re-encrypt an updated plaintext file to its .enc twin before committing
git-crypt-helper.sh sync-to-enc .env
git-crypt-helper.sh sync-to-enc docs/.env
```

The helper verifies that the target file is listed in `.gitignore` before syncing, prevents accidental overwrites if a twin is out of date, and ensures secrets never leak into Git commits unencrypted.

### Detecting Locked Blobs and Cleaning Inputs

When a repository is cloned by someone without the symmetric key, files matched by `.gitattributes` (such as `input.txt`) are checked out as raw encrypted binary blobs. If an AoC solution tries to read such a file as UTF-8 text, it will immediately crash with decoding errors or nonsensical parsing failures.

To handle this gracefully:

1. **In-Code Detection**: Our shared helper library provides `ac.is_git_crypt_locked(path)` in `src/aoc_common/aoc_commons.py`. It inspects the file header for the `\x00GITCRYPT\x00` signature. If a locked blob is detected, the CLI knows not to treat it as valid puzzle data.
2. **Scrubbing Locked Blobs**: Anyone who clones the repo to solve puzzles with their own data can run:
   ```bash
   uv run aoc clean-inputs       # or: make clean-inputs
   ```
   This command scans the workspace, finds any locked `git-crypt` `input*.txt` files, and removes them safely — while preserving all sample input files and any unlocked real inputs. Once cleaned, running `uv run aoc fetch <target>` or executing a Template v3 script will fetch their own personal puzzle input into `input/input.txt`.

### Useful Git-Crypt Commands

```bash
git-crypt status # check what will be encrypted
```

<img src="{{'/assets/images/git-crypt-status.png' | relative_url }}" alt="Git-Crypt Status" style="width:600px;" />

```bash
git-crypt status -e # show only encrypted [and should be encrypted]
```

<img src="{{'/assets/images/git-crypt-status-e.png' | relative_url }}" alt="Git-Crypt Status - Encrypted Only" style="width:600px;" />

```bash
git-crypt lock # lock all files locally. (This happens transparently on push to remote.)
git-crypt unlock [path/to/keyfile] # unlock all encrypted local files. (Transparent on pull.)
```

### Cloning an Existing Repo with Encrypted Files

For a **newly cloned repo** (e.g. on a new machine), you will need to unlock any encrypted files manually. You do this with `git-crypt unlock` and pass in your key:

```bash
git-crypt unlock ../git-crypt-key
```

Once unlocked, restore any parallel secrets:

```bash
git-crypt-helper.sh sync-from-enc
```

### Retrospective Encryption

Of course, if you're **looking to encrypt having previously staged, committed, or pushed files**, those files will not be encrypted automatically. But you can retrospectively fix this:

```bash
git-crypt status -f  # FIX, i.e. retrospectively encrypt files that were previously staged / committed
git commit -m "My retrofix"
git push
```

Caution: in this case, your Git history will still contain the unencrypted versions. You can deal with this using tools like `git-filter-repo` if you need to remove old versions from the commit history completely.

### What Does It Look Like in GitHub?

After check-in and push, your input files will be visible in your GitHub repo. But the contents of the files will not be readable. You can download them in raw format, but if you open them, they'll look something like this...

<img src="{{'/assets/images/encrypted-input.png' | relative_url }}" alt="Encrypted Input File" style="width:600px;" />

### Troubleshooting

If you happen to change the location of your `git-crypt` executable, Git's smudge and clean filters might report an error. For example, this can happen if a repo was originally cloned in Windows and then opened directly in WSL.

In this scenario, you can fix your `.git/config` settings to invoke `git-crypt` directly:

```text
[filter "git-crypt"]
	smudge = \"git-crypt\" smudge
	clean = \"git-crypt\" clean
```
