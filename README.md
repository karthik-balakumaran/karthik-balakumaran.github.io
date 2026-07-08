# Deploy to GitHub Pages (user site)

This repository contains a static portfolio site. The included `deploy_user_site.sh` script will create a user-site repository named `karthik-balakumaran.github.io` under the GitHub account `Karthik-Balakumaran` and push the current contents so the site is served at:

  https://karthik-balakumaran.github.io

Prerequisites
- `git` installed and configured locally
- `gh` (GitHub CLI) installed and authenticated (`gh auth login`)

Quick steps (automated)

1. Make the deploy script executable:

```bash
chmod +x deploy_user_site.sh
```

2. Run the script from the repository root:

```bash
./deploy_user_site.sh
```

What the script does
- Verifies `gh` and `git` are available and that `gh` is authenticated
- Creates `Karthik-Balakumaran/karthik-balakumaran.github.io` (public) if it doesn't exist
- Adds a remote named `userpage` and pushes the current `main` branch

Manual commands (if you prefer to run steps yourself)

```bash
# create a new user-site repo and push current directory (recommended)
gh repo create Karthik-Balakumaran/karthik-balakumaran.github.io --public --source=. --remote=userpage --push

# or, if the repo already exists
git remote add userpage git@github.com:KarthikBalakumaran/karthikbalakumaran.github.io.git
git push -u userpage main
```

Notes
- The script uses `main` as the branch to publish. If your primary branch is named differently, set the `BRANCH` environment variable before running the script, for example:

```bash
BRANCH=main ./deploy_user_site.sh
```

If you want, I can run the script for you here — I'll need `gh` authentication available in this environment.
