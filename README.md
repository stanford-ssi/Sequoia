# Sequoia | an open source, 3U CubeSat
Welcome to our GitHub!

Lets get started! Get this repository and all of its submodules by running 
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
