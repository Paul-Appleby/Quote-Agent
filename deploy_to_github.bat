@echo off
echo ========================================
echo WAXD Sales Agent - GitHub Deployment
echo ========================================
echo.

echo Please follow these steps to deploy to GitHub:
echo.
echo 1. Go to https://github.com and sign in
echo 2. Click the "+" icon and select "New repository"
echo 3. Name it: waxd-sales-agent
echo 4. Make it Public or Private (your choice)
echo 5. DO NOT initialize with README, .gitignore, or license
echo 6. Click "Create repository"
echo.
echo After creating the repository, GitHub will show you commands.
echo Copy the repository URL and run the following commands:
echo.

set /p repo_url="Enter your GitHub repository URL (e.g., https://github.com/username/waxd-sales-agent.git): "

if "%repo_url%"=="" (
    echo No URL provided. Please run this script again with a valid URL.
    pause
    exit /b 1
)

echo.
echo Adding remote origin...
git remote add origin %repo_url%

echo.
echo Setting main branch...
git branch -M main

echo.
echo Pushing to GitHub...
git push -u origin main

echo.
echo ========================================
echo Deployment completed!
echo ========================================
echo.
echo Your repository is now available at: %repo_url%
echo.
echo Next steps:
echo 1. Update the README.md with your actual repository URL
echo 2. Set up your production environment
echo 3. Configure GoHighLevel webhook
echo.
pause 