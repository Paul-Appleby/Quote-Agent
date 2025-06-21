# Deploy to GitHub - Step by Step Guide

## Option 1: Using GitHub Web Interface (Recommended)

1. **Go to GitHub.com** and sign in to your account

2. **Create a new repository**:
   - Click the "+" icon in the top right corner
   - Select "New repository"
   - Name it: `waxd-sales-agent` or `sales-agent`
   - Make it Public or Private (your choice)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
   - Click "Create repository"

3. **Copy the repository URL** that GitHub provides (it will look like):
   ```
   https://github.com/yourusername/waxd-sales-agent.git
   ```

4. **Add the remote origin** to your local repository:
   ```bash
   git remote add origin https://github.com/yourusername/waxd-sales-agent.git
   ```

5. **Push your code**:
   ```bash
   git branch -M main
   git push -u origin main
   ```

## Option 2: Using GitHub CLI (if installed)

1. **Install GitHub CLI** (if not already installed):
   - Windows: Download from https://cli.github.com/
   - Or use: `winget install GitHub.cli`

2. **Authenticate with GitHub**:
   ```bash
   gh auth login
   ```

3. **Create and push repository**:
   ```bash
   gh repo create waxd-sales-agent --public --source=. --remote=origin --push
   ```

## Option 3: Manual Git Commands

If you prefer to do it manually:

```bash
# Add remote origin (replace with your actual repository URL)
git remote add origin https://github.com/yourusername/waxd-sales-agent.git

# Set the main branch
git branch -M main

# Push to GitHub
git push -u origin main
```

## After Deployment

Once your code is on GitHub:

1. **Update the README.md** with your actual repository URL
2. **Set up GitHub Pages** (optional) for documentation
3. **Configure GitHub Actions** for CI/CD (optional)
4. **Add collaborators** if working with a team

## Repository URL Update

After creating the repository, update the clone URL in README.md:

```markdown
git clone https://github.com/yourusername/waxd-sales-agent.git
```

## Security Notes

- Make sure your `.env` file is in `.gitignore` (it should be)
- Never commit API keys or sensitive data
- Consider using GitHub Secrets for environment variables in CI/CD

## Next Steps

1. Set up your production environment
2. Configure your GoHighLevel webhook to point to your deployed server
3. Test the webhook integration
4. Monitor the application logs and performance 