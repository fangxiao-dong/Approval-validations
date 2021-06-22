import os
import os.path
from collections import defaultdict
from typing import List

class ValidateApprovals(object):
    """A class to represent logics of validating approvals for a given repo/directory"""

    def __init__(self, repo_dir: str, approvers_input: str='', changed_files_input: str=''):
        """
            repo_dir: the directory of the repo to validate
            dir_maps: A dictionary that includes each directory information.
                k: normalized path to the current directory. Root/repo directory is represented by '.'
                v: A list includes 2 sub lists:
                    1. a list of dependencies
                    2. a list of direct owners
            approvers_input: comma separated approvers from the input of the affected directories
            changed_files_input: comma separated paths from the input starting from the root(excluding the repo name itself) of the repo to the changed files
        """

        self.repo_dir = repo_dir
        self.dir_maps = defaultdict(lambda: [[], []])
        self.approvers_input = approvers_input
        self.changed_files_input = changed_files_input

    def build_dir_maps(self):
        '''
            Build the directory maps by extracting information when walking through the file strcture
            and store them in a dictionary
        '''
        # os.walk uses DFS to recrusively traverse the file structure
        for root, _, files in os.walk(self.repo_dir):
            # Normalize the dirctory name as key of the dict to match the directory used by the DEPENDENCIES file 
            normalized_dir = os.path.relpath(root, self.repo_dir)
            self.process_meta_files('DEPENDENCIES', root, normalized_dir, files)
            self.process_meta_files('OWNERS', root, normalized_dir, files)
    
    def process_meta_files(self, file: str, root_dir: str, normalized_dir: str, files: List[str]):
        '''process the meat data files'''

        if file in files:
            file_path = os.path.join(root_dir, file)
            with open(file_path, 'r') as f:
                metas = [l.rstrip('\n').strip() for l in f]
            
            if file == 'DEPENDENCIES':
                self.dir_maps[normalized_dir][0].extend(metas)
            elif file == 'OWNERS':
                self.dir_maps[normalized_dir][1].extend(metas)
        else:
            if file == 'DEPENDENCIES':    
                self.dir_maps[normalized_dir][0].extend([])
            elif file == 'OWNERS':
                self.dir_maps[normalized_dir][1].extend([])

    def get_dir_all_owners(self, dir: str):
        '''Get both direct and ancestor owners of the given directory'''

        direct_owners = self.dir_maps[dir][1]
        ancestor_owners = []
        # Any directory name starts with given directory or the root directory is the given's dirs anestor dir
        [ancestor_owners.extend(self.dir_maps[d][1]) for d in self.dir_maps if (dir.startswith(d) or d == '.') and len(self.dir_maps[d][1]) != 0]
        # Use set because direct owners and ancestor owners may bear the same name
        dir_all_owners = set(direct_owners + ancestor_owners)
        return dir_all_owners

    def get_dir_upstream_deps(self, dir: str):
        '''
            Get the upstream dependencies directories of the given directory if the file(s) under the given directory is changed.
            Upstream dependency is defined as directories that need approvals when the given dir that the upstream dep depends on is changed.
            It also includes the directory in which file is chagned directly.
        '''

        dir_upstream_deps = [dir]
        for d, (deps, _) in self.dir_maps.items():
            if dir in deps:
                dir_upstream_deps.append(d)
        return dir_upstream_deps

    def get_affected_dirs_input(self):
        '''parse comma seperated file names input to find the affected directories'''

        # Use set because a user may input same changed files multiple times
        trimmed_files = {fi.strip() for fi in self.changed_files_input.split(',')}
        affected_dirs = {os.path.dirname(tf) for tf in trimmed_files}

        return affected_dirs

    def get_approvers_input(self):
        '''parse comma seperated approvers input to find all approvers'''

        # Use set because a user may input same approvers multiple times
        trimmed_approvers = set([ai.strip() for ai in self.approvers_input.split(',')])

        return trimmed_approvers

    def validate_approvals(self):
        '''validate if given affected dirs have sufficient approvals. Print "Approved" or "Insufficient approvals"'''
        
        self.build_dir_maps()

        affected_dirs = self.get_affected_dirs_input()
        approvers = self.get_approvers_input()
        
        for ad in affected_dirs:
            upstream_deps = self.get_dir_upstream_deps(ad)
            for ud in upstream_deps:
                all_owners = self.get_dir_all_owners(ud)
                if not any(a in all_owners for a in approvers):
                    print('Insufficient approvals')
                    return False
        print('Approved')
        return True
        
