- 버전 컨트롤에 대한 기본적인 사항으로, 별다른 요구사항이 없을때 아래사항을 따른다. 


### Basic Git Workflow
```
# Clone repository
git clone <url>

# Create feature branch
git checkout -b feature/my-feature

# Stage changes
git add .
git add file.cpp

# Commit
git commit -m "Add new feature"

# Push to remote
git push origin feature/my-feature

# View commit history
git log --oneline
git log --graph --all --oneline

# View changes
git diff
git diff --staged
```

### Code Review Workflow
```
# Create pull request
gh pr create --title "Feature" --body "Description"

# Review changes
git show <commit>

# Squash commits before merge
git rebase -i HEAD~3

# Merge to main
git checkout main
git pull origin main
git merge feature/my-feature
git push origin main
```