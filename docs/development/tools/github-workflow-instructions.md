# GitHub Workflow Setup Instructions

You're facing an OAuth scope restriction when trying to push GitHub workflow files. GitHub restricts workflow file updates for security reasons. Here's how to add them properly:

## Option 1: Use the GitHub Web Interface (Recommended)

1. Go to [your repository](https://github.com/datacosmos-br/dc-api-x)
2. Navigate to the `.github/workflows` directory
3. For each workflow file:
   - Click "Add file" → "Create new file"
   - Name the file (e.g., `docs.yml`)
   - Copy and paste the content from the corresponding file in the `/home/marlonsc/pyauto/temp_workflows/` directory
   - Commit directly to the main branch

## Option 2: Use a Personal Access Token with Workflow Scope

1. Go to [GitHub Personal Access Token settings](https://github.com/settings/tokens)
2. Create a new token with `workflow` scope (and other needed scopes)
3. Use this token for git authentication:

   ```bash
   git remote set-url origin https://YOUR_USERNAME:YOUR_TOKEN@github.com/datacosmos-br/dc-api-x.git
   git checkout main
   git push origin main
   ```

## Option 3: Create a Pull Request from the Web Interface

1. Go to [your repository](https://github.com/datacosmos-br/dc-api-x)
2. Click on "Pull requests" tab
3. Click "New pull request"
4. Set the base branch to `main` and compare branch to `config-without-workflows`
5. Create the pull request
6. After merging, add workflow files using the GitHub web interface

## Workflow Files

I've saved all your workflow files in:

- The `/home/marlonsc/pyauto/temp_workflows/` directory (individual files)
- The `/home/marlonsc/pyauto/github_workflows.zip` file (zip archive)

## Which Files to Add

Add these workflow files:

1. `docs.yml` - Documentation build and deployment
2. `greetings.yml` - Welcome messages for contributors
3. `label.yml` - Automatic PR labeling
4. `python-workflow.yml` - Main CI/CD pipeline
5. `release.yml` - Release automation
6. `security-scans.yml` - Security scanning
7. `stale.yml` - Stale issue management
8. `summary.yml` - Issue summarization
