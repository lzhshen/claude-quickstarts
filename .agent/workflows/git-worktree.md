---
name: git-worktree
aliases: [gwt]
description: Use when starting feature work that needs isolation - creates isolated git worktrees using parallel directory structure
---

# Git Worktree Manager

## Overview

Git worktrees create isolated workspaces sharing the same repository, allowing work on multiple branches simultaneously.

**Core principle:** Systematic directory selection with parallel structure = reliable isolation.

**Announce at start:** "I'm using the git-worktree skill to set up an isolated workspace."

## Directory Selection Process

This skill uses **parallel directory structure** for worktrees:

```
/mnt/d/dev/
├── parlant-studio-01/                          # Main worktree
├── parlant-studio-01-<feature-name>/          # Feature worktree
├── parlant-studio-01-<bugfix-name>/           # Bugfix worktree
└── ...
```

All worktrees are created as **sibling directories** to the main project.

## Safety Verification

### Verify .gitignore Configuration

Before creating worktrees, ensure patterns are in `.gitignore`:

```bash
check_gitignore_for_worktrees() {
  local patterns=(
    "parlant-studio-01-*"
  )

  for pattern in "${patterns[@]}"; do
    if ! grep -q "^$pattern$" .gitignore; then
      echo "Pattern '$pattern' not found in .gitignore"
      return 1
    fi
  done

  return 0
}
```

**If patterns not found:**
1. Add to .gitignore immediately
2. Commit the change
3. Proceed with worktree creation

**Why critical:** Prevents accidentally committing worktree contents to repository.

## Commands

### Create Worktree

**Usage:** `/git-worktree create <branch-name> [options]`

Creates a new worktree with parallel directory structure.

**Options:**
- `--no-setup`: Skip automatic dependency installation
- `--no-test`: Skip baseline test verification
- `--no-push`: Skip pushing branch to remote

**Process:**

```bash
# 1. Determine paths
project_name="parlant-studio-01"
worktree_dir="/mnt/d/dev/${project_name}-${BRANCH_NAME}"

# 2. Create worktree (creating new branch)
git worktree add "$worktree_dir" -b "$BRANCH_NAME"

cd "$worktree_dir"

# 3. Run project setup (if not --no-setup)
if [ -f package.json ]; then npm install; fi
if [ -f requirements.txt ]; then
  if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
  fi
  pip install -r requirements.txt
fi

# 4. Run baseline tests (if not --no-test)
npm run test  # or other test command
# Report results

# 5. Push branch to remote (if not --no-push)
git push -u origin "$BRANCH_NAME"

echo "Worktree ready at $worktree_dir"
```

### List Worktrees

**Usage:** `/git-worktree list`

```bash
echo "=== Local Worktrees ==="
git worktree list

echo ""
echo "=== Parallel Structure Worktrees ==="
ls -d /mnt/d/dev/parlant-studio-01-*/ 2>/dev/null || echo "None found"
```

### Remove Worktree

**Usage:** `/git-worktree remove <worktree-name>`

```bash
# worktree-name can be:
# - Full path: /mnt/d/dev/parlant-studio-01-feature-x
# - Short name: feature-x (prepends parlant-studio-01-)

if [[ "$WORKTREE" != /* ]]; then
  WORKTREE="/mnt/d/dev/parlant-studio-01-$WORKTREE"
fi

if [ ! -d "$WORKTREE" ]; then
  echo "Error: Worktree directory not found: $WORKTREE"
  exit 1
fi

# Remove worktree
git worktree remove --force "$WORKTREE"

# Optionally, delete the directory (if not auto-removed)
if [ -d "$WORKTREE" ]; then
  rm -rf "$WORKTREE"
fi

echo "Worktree removed: $WORKTREE"
```

### Clean Merged Worktrees

**Usage:** `/git-worktree clean [options]`

Removes worktrees for branches that have been merged to main.

**Options:**
- `--dry-run`: Show what would be removed without removing
- `--force`: Skip confirmation prompts

**Process:**

```bash
# 1. Get list of parallel worktrees
worktrees=$(find /mnt/d/dev -maxdepth 1 -type d -name "parlant-studio-01-*")

# 2. Check each worktree's branch status
for worktree in $worktrees; do
  branch=$(basename "$worktree" | sed 's/parlant-studio-01-//')

  # Check if branch is merged to main
  if git branch --merged main | grep -q "^\s*$branch$"; then
    echo "Branch '$branch' is merged - removing $worktree"

    if [ "$DRY_RUN" != "true" ]; then
      git worktree remove --force "$worktree" 2>/dev/null
      rm -rf "$worktree"
    fi
  fi
done
```

### Create Pull Request

**Usage:** `/git-worktree pr <title> [options]`

Creates a GitHub pull request from current worktree branch.

**Options:**
- `--body "description"`: PR description
- `--draft`: Create as draft PR
- `--base <branch>`: Target branch (default: main)

**Process:**

```bash
# Ensure we're in a worktree
if [ ! -f .git ]; then
  echo "Error: Not in a git worktree"
  exit 1
fi

# Get current branch
current_branch=$(git rev-parse --abbrev-ref HEAD)

# Create PR using GitHub CLI
gh pr create \
  --title "$PR_TITLE" \
  --body "$PR_BODY" \
  --base "$BASE_BRANCH" \
  ${DRAFT:+--draft}
```

## Quick Reference

| Command | Action |
|---------|--------|
| `/gwt create feature-auth` | Create worktree for `parlant-studio-01-feature-auth` |
| `/gwt list` | List all worktrees (git and parallel) |
| `/gwt remove feature-auth` | Remove specific worktree |
| `/gwt clean` | Remove merged worktrees |
| `/gwt pr "Add authentication"` | Create PR from current worktree |

## Example Workflows

### Starting Feature Work

```bash
# Main project directory
cd /mnt/d/dev/parlant-studio-01

# Create feature worktree (creates parlant-studio-01-user-profile)
/gwt create user-profile

# Output:
# Worktree ready at /mnt/d/dev/parlant-studio-01-user-profile
# Tests passing (24 tests, 0 failures)
# Ready to implement user-profile feature
```

### Multiple Features in Parallel

```
/mnt/d/dev/
├── parlant-studio-01/                          # main branch
├── parlant-studio-01-user-profile/            # feature: user profile
├── parlant-studio-01-payment-gateway/         # feature: payment
└── parlant-studio-01-bugfix-auth-redirect/    # bugfix: auth redirect
```

### Creating PR from Worktree

```bash
cd /mnt/d/dev/parlant-studio-01-user-profile

# Create PR
/gwt pr "feat: Add user profile management UI"

# Output:
# Creating pull request for branch 'user-profile' into 'main'
# Pull request created: https://github.com/user/repo/pull/123
```

### Cleaning Up Merged Worktrees

```bash
cd /mnt/d/dev/parlant-studio-01

# Check what would be removed
/gwt clean --dry-run

# Output:
# These worktrees will be removed:
#   /mnt/d/dev/parlant-studio-01-old-feature
#   /mnt/d/dev/parlant-studio-01-bugfix-123

# Actually remove them
/gwt clean
```

## Safety Checks

### Before Creating Worktree

1. **Verify .gitignore patterns exist**
   - `parlant-studio-01-*` must be in .gitignore

2. **Check disk space**
   - Each worktree is a full working copy

3. **Validate branch name**
   - Must be valid git branch name
   - Cannot conflict with existing branch

### Before Removing Worktree

1. **Check for uncommitted changes**
   ```bash
   if [ -n "$(git status --porcelain)" ]; then
     echo "Warning: Uncommitted changes in worktree"
     read -p "Proceed with removal? [y/N] " confirm
   fi
   ```

2. **Verify branch is merged (for clean command)**
   ```bash
   if ! git branch --merged main | grep -q "$branch"; then
     echo "Warning: Branch not merged to main"
   fi
   ```

## Requirements

### Required Tools
- `git` (with worktree support - version 2.5+)
- `gh` (GitHub CLI)
- `find` (for listing/cleaning worktrees)

### GitHub Configuration
```bash
# Ensure gh auth is configured
gh auth status
```

## Common Issues & Solutions

### Issue: Worktree directory already exists
**Solution:** Remove the directory or choose different branch name

### Issue: Branch already exists
**Solution:** Use existing branch or delete it first: `git branch -D <branch>`

### Issue: Tests fail in new worktree
**Solution:**
- Check dependencies installed correctly
- Verify environment variables
- Compare with main worktree configuration

### Issue: .gitignore patterns missing
**Solution:**
```bash
echo "parlant-studio-01-*" >> .gitignore
git add .gitignore
git commit -m "chore: Add worktree patterns to .gitignore"
```

## Best Practices

1. **Use descriptive branch names**
   - Good: `user-profile`, `payment-gateway`, `bugfix-auth-redirect`
   - Avoid: `feature1`, `test`, `tmp`

2. **Run tests after creation**
   - Ensures baseline is clean
   - Prevents confusion with new bugs

3. **Push branches to remote**
   - Enables CI/CD testing
   - Facilitates collaboration
   - Allows PR creation

4. **Clean up merged worktrees**
   - Frees disk space
   - Reduces confusion
   - Use `/gwt clean --dry-run` first

5. **Document worktree purpose**
   - PR description should explain changes
   - Use meaningful commit messages
   - Update README if needed

## Red Flags

**Never:**
- Create worktree without .gitignore verification
- Proceed with failing tests without investigation
- Remove worktree with uncommitted changes (without backup)
- Use non-descriptive branch names

**Always:**
- Verify .gitignore before first worktree creation
- Run baseline tests after creation
- Push branches to remote
- Clean up merged worktrees regularly
