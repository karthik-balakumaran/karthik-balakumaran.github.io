#!/usr/bin/env bash
set -euo pipefail

REPO_OWNER="KarthikBalakumaran"
REPO_NAME="karthikbalakumaran.github.io"
REMOTE_NAME="userpage"
BRANCH="${BRANCH:-main}"

echo "Preparing to publish repository to GitHub Pages user site: ${REPO_OWNER}/${REPO_NAME}"

if ! command -v gh >/dev/null 2>&1; then
  echo "Error: gh (GitHub CLI) is not installed. Install from https://cli.github.com/" >&2
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "Error: git is not installed." >&2
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "gh is not authenticated. Run: gh auth login" >&2
  exit 1
fi

# Create repo if it doesn't exist
if gh repo view "${REPO_OWNER}/${REPO_NAME}" >/dev/null 2>&1; then
  echo "Repository ${REPO_OWNER}/${REPO_NAME} already exists. Adding remote and pushing..."
  git remote remove "${REMOTE_NAME}" 2>/dev/null || true
  git remote add "${REMOTE_NAME}" "git@github.com:${REPO_OWNER}/${REPO_NAME}.git"
  git push -u "${REMOTE_NAME}" "${BRANCH}"
else
  echo "Creating repository ${REPO_OWNER}/${REPO_NAME} and pushing current directory..."
  gh repo create "${REPO_OWNER}/${REPO_NAME}" --public --source=. --remote="${REMOTE_NAME}" --push
fi

echo "Published. Visit: https://${REPO_OWNER}.github.io"
