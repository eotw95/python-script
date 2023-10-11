import os
import re
import sys
from collections import OrderedDict;

class ExecutePatchAndCommit():
    def checkApplyPatch(self, patchFileDirPath, patchFileNames) :
        print("patchFileDirPath="+patchFileDirPath);
        print("patchFile count=%d" % len(patchFileNames));
        print("patchFileNames=%s" % str(patchFileNames));
        
        for patchFileName in patchFileNames :
            patchFilePath = os.path.join(patchFileDirPath, patchFileName);
            if not os.path.isfile(patchFilePath) :
                print("FAILED: patch file does not exist");
            else :
                print(f"### Start check {patchFileName}")
                # cd target repo
                targetRepoPath = None
                with open(patchFilePath, "r") as patch :
                    lines = patch.readlines();
                    for line in lines :
                        if line.startswith("GIT_APPLY_TOP_DIR=") :
                            targetRepoPath = line.split("=")[1].strip()
                            print(f"targetRepoPath={targetRepoPath}")
                targetRepoAbsPath = os.path.abspath(targetRepoPath)
                curDirPath = os.getcwd();

                print(f"cd {targetRepoAbsPath}");
                os.chdir(targetRepoAbsPath);

                # git apply --check
                print(f"git apply --check {patchFilePath}")
                applyPatchResult = os.system(f"git apply --check {patchFilePath}");
                if applyPatchResult != 0:
                    print(f"FAILED: Check apply failed {patchFileName}");
                    exit();
                print(f"Check apply success {patchFileName} ");

                # WA: Back to start directory
                # During the second iteration in the for loop, 
                # there is a bug where targetRepoPath gets concatenated to targetRepoAbsPath. 
                # As a temporary workaround, Back to the start directory.
                os.chdir(curDirPath);

    def execute(self, patchFileDirPath, patchFileNames) :
        for patchFileName in patchFileNames :
            patchFilePath = os.path.join(patchFileDirPath, patchFileName);
            if not os.path.isfile(patchFilePath) :
                print("FAILED: patch file does not exist");
                exit();
            else :
                print(f"### Start executePatchAndCommit {patchFileName}")
                # cd target repo
                targetRepoPath = None
                with open(patchFilePath, "r") as patch :
                    lines = patch.readlines();
                    for line in lines :
                        if line.startswith("GIT_APPLY_TOP_DIR=") :
                            targetRepoPath = line.split("=")[1].strip();
                targetRepoAbsPath = os.path.abspath(targetRepoPath)
                curDirPath = os.getcwd();

                print(f"cd {targetRepoAbsPath}");
                os.chdir(targetRepoAbsPath);

                # git apply
                print(f"git apply {patchFilePath}");
                applyResult = os.system(f"git apply {patchFilePath}");
                if applyResult != 0 :
                    print(f"FAILED: git apply failed {patchFilePath}");
                    exit();

                # git add
                filePattern = r"diff --git a/(.+) b/\1";
                with open(patchFilePath, "r") as patch :
                    lines = patch.readlines();
                    for line in lines :
                        match = re.match(filePattern, line);
                        if match :
                            targetFile = match.group(1);
                            print(f"git add {targetFile}");
                            addResult = os.system(f"git add {targetFile}");
                            if addResult != 0 :
                                print(f"FAILED: git add failed {targetFile}");
                                exit();

                # git commit
                subject = None
                testReport = None
                changeId = None
                subjectPattern = r"Subject: (.+)"
                testReportPattern = r"\[Test Report\]\n(.+)"
                changeIdPattern = r"Change-Id: (.+)"

                with open(patchFilePath, "r") as patch :
                    lines = patch.readlines();
                    for line in lines :
                        # Subject:
                        if line.startswith('Subject:'):
                            subject = re.sub(r"Subject:|\[.*?\]", "", line).strip();

                        # [Test report]
                        testReportMatch = re.match(testReportPattern, line);
                        if testReportMatch :
                            testReport = testReportMatch.group(1).strip();

                        # Change Id:
                        changeIdMatch = re.match(changeIdPattern, line);
                        if changeIdMatch :
                            changeId = changeIdMatch.group(1).strip();

                commitMessage = None            
                if changeId == None :
                    commitMessage = f"git commit -m '{subject}' -m '({patchFileName})' -m 'Test: {testReport}'";
                else :
                    commitMessage = f"git commit -m '{subject}' -m '({patchFileName})' -m 'Test: {testReport}' -m 'Change-Id: {changeId}'";
                print(commitMessage);
                commitResult = os.system(commitMessage);
                if commitResult != 0 :
                    print(f"FAILED: git commit failed [{commitMessage}]");
                    exit();

                # Back to start directory
                os.chdir(curDirPath);

def main(args):
    if len(args) < 3 :
        raise Exception("Invalid Parameter");
        return;

    # arg 1: base directory of patch files
    if not os.path.isdir(args[1]) :
        raise Exception(f"Base directory of patch files is not found: {args[1]}")
        return;
    patchFileDirPath = os.path.abspath(args[1]);

    # arg 2: patch files
    patchFileNames = args[2].split("####");
    if len(patchFileNames) == 0 :
        raise Exception("Patch files is empty")
        return;
    
    # check apply patch
    ExecutePatchAndCommit().checkApplyPatch(patchFileDirPath, patchFileNames);

    # execute patch and commit
    ExecutePatchAndCommit().execute(patchFileDirPath, patchFileNames);

main(sys.argv);