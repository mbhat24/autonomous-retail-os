# Safe GitHub Push Instructions

Do not put tokens in code, docs, commit messages, shell history, or chat.

## If a token was exposed

1. Go to GitHub token settings.
2. Revoke the exposed token immediately.
3. Create a new token only if needed.
4. Prefer `gh auth login` over manually copying tokens.

## Initialize and Push

```bash
git init
git add .
git commit -m "Initial autonomous retail OS implementation"
gh repo create autonomous-retail-os --private --source=. --remote=origin --push
```

If you already created the GitHub repository:

```bash
git remote add origin git@github.com:<your-user>/autonomous-retail-os.git
git push -u origin main
```

Use SSH or GitHub CLI authentication. Do not paste tokens into remote URLs.
