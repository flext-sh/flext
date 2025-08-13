#!/usr/bin/env bash
# Bulk commit/merge/push to main in a submodule without invoking local hooks/venvs
set -u -o pipefail

repo_top="$(git rev-parse --show-toplevel)"
repo_name="$(basename "$repo_top")"
summary_file="${GIT_TOPLEVEL:-$repo_top}/.git-tools/submodule-push-summary.txt"
mkdir -p "$(dirname "$summary_file")"

current_branch_raw="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo HEAD)"
current_branch="$current_branch_raw"
if [[ $current_branch == "HEAD" ]]; then
	current_branch="detached"
fi

echo "[SUBMODULE: $repo_name | BRANCH: $current_branch]"

# If detached, create a temp branch to hold commits
if [[ $current_branch == "detached" ]]; then
	tmp_branch="bulk/$(date +%Y%m%d-%H%M%S)"
	git checkout -B "$tmp_branch" >/dev/null 2>&1 || true
	current_branch="$tmp_branch"
fi

# Fetch and commit local changes, bypassing hooks to avoid per-repo venvs
(git fetch --all --prune || true) >/dev/null 2>&1

git add -A || true
if ! git diff --cached --quiet --ignore-submodules --; then
	git commit --no-verify -m "chore: bulk save before merge to main" || echo "COMMIT_FAILED $repo_name on $current_branch" | tee -a "$summary_file" >&2
fi

main_branch="main"
# Ensure local main exists and tracks remote if available
if git show-ref --verify --quiet refs/heads/$main_branch; then
	:
else
	if git show-ref --verify --quiet refs/remotes/origin/$main_branch; then
		git checkout -B $main_branch origin/$main_branch >/dev/null 2>&1 || true
	else
		git checkout -B $main_branch >/dev/null 2>&1 || true
	fi
fi

# Merge current branch into main when appropriate
if [[ $current_branch != "$main_branch" ]]; then
	git checkout $main_branch >/dev/null 2>&1 || true
	(git pull --rebase origin $main_branch || true) >/dev/null 2>&1
	if git merge --no-ff -m "chore: merge $current_branch into main (bulk)" "$current_branch" >/dev/null 2>&1; then
		echo "Merged $current_branch -> main"
	else
		echo "MERGE_CONFLICT $repo_name merging $current_branch into main" | tee -a "$summary_file" >&2
		git merge --abort >/dev/null 2>&1 || true
	fi
else
	git checkout $main_branch >/dev/null 2>&1 || true
	(git pull --rebase origin $main_branch || true) >/dev/null 2>&1
fi

# Ensure upstream and push
if git rev-parse --abbrev-ref --symbolic-full-name @{u} >/dev/null 2>&1; then
	:
else
	git branch --set-upstream-to=origin/$main_branch $main_branch >/dev/null 2>&1 || true
fi

(git push origin $main_branch || true) >/dev/null 2>&1

exit 0
