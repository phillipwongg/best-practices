Below are basic steps you can take to create a pull workflow for your github repository.  This flow assumes you already have a repository.

## Step 1 - UPDATE TO the master branch
In the gitshell and root directory of your repo, type `git checkout master` and then `git pull origin master`  to get the latest master code.

## Step 2 - Create a new branch
Type `git checkout -b name-of-branch`

## Step 3 - make changes and COMMIT
Work to address the branch's issue or new feature. Add your changes with `git add .` and make commit(s) with `git commit -m`. 

When the issue/feature is complete and ready for review, you can close the issue with a commit by typing  `git commit -m "fixes #N"`  with #N being the number of the issue.

## Step 4 - PUSH BRANCH
Type `git push origin [name-of-branch]`

## Step 5 - create a pull request in github

## Step 6 - Merge pull request with github/origin master 

## Step 7 - checkout local master, pull in from upstream/origin
`git checkout master`
`git pull origin master`

## step 8 - Delete branch
To delete the branch locally, run `git branch -d {name-of-branch}`
