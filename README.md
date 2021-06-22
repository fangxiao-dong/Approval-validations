# Validate Approvals
This is a CLI tool to validate in a repo if changes in the given directories with the given approvers result in sufficient approvals. Print "Approved" if sufficient; Otherwise, print "Insufficient approvals".

Approval rules are:
- A change is approved if all of the affected directories are approved.
- A directory is considered to be affected by a change if either: (1) a file in that directory was changed, or (2) a file in a (transitive) dependency directory was changed.
    - In case (1), we only consider changes to files directly contained within a directory, not files in subdirectories.
	- Case (2) includes transitive changes, so a directory is also affected if a dependency of one of its dependencies changes, etc.
- A change to a file in a directory has approval if at least one engineer listed in an OWNERS file in that directory or any of its ancestor directories has approved it

## Usage

### Prerequisites
1. This tool runs under Python 3 environment and was developed using Python 3.7. Make sure your local environment has Python 3.7+ installed.
2. This tool uses all internal Python libraries so no need to install additional dependencies as long as your environment has Python 3.7 installed.
2. The CLI tool is located in the `bin/` directory and is named `validate_approvals`. Before running it, check if that file has executable bit turned on in your environment. If not, you may need to run `chomod` to grant `x` right to the file to make it executable on your local environment.

### Run
First `cd` intot he `bin/` directory or running the CLI by specifying the path to the CLI. You can then run it with the following command:
```
$ ./validate_approvals [-h] [--repo-dir REPO_DIR] --approvers APPROVERS --changed-files CHANGED_FILES
```
Before using it for validation, it is suggested you run `./validate_approvals -h` for checking its usage.

There are 2 usages depending on if you want to specify the path to the repo on the command line:
1. Specifying the repo to check, for example if the current working directory is `bin/`:
```
$ ./validate_approvals --repo-dir ../tests/fixture/repo_root --approvers alovelace,ghopper --changed-files src/com/twitter/follow/Follow.java,src/com/twitter/tweet/Tweet.java
```

2. If not specifying the repo on the CLI, you will need to copy the repo to the `bin/` directory as it assumes there is only one directory to represent the repo to validate. When you want to check another, remove the old one and copy the new one to the `bin/` directory.
```
$ ./validate_approvals --approvers alovelace,ghopper --changed-files src/com/twitter/follow/Follow.java,src/com/twitter/tweet/Tweet.java
```

### Run Tests
You can run all the tests by issuing the following from the root of this project:
```
$ python -m unittest tests/validate_approvals_test.py
```