# Welcome to Sequoia's GitHub!

Lets get started. Get this repository and all of its submodules by running 
this command in your terminal:
```
$: git clone --recursive https://github.com/stanford-ssi/sequoia.git
```
This makes a copy of everything in this repository and all of its submodules.

Next, make a new branch for yourself: 
```
$: git checkout -b <YOUR_NAME>
```
Now, let's get to editing! 

Update all of the submodules with code from github:
```
$: git submodule update --remote --merge
```

Push to your branch
```
$: git push --recurse-submodules=on-demand
```

### Useful Documentation
[Git Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
