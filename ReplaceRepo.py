import os

class ReplaceRepo():
    def execute(self) :
        # Delete repo
        targetRepoPaths = [
            "dummy/sample1",
            "dummy/sample2",
            "dummy/sample3",
        ];

        for path in targetRepoPaths :
            if path == "dummy/sample3" :
                # Is case sample3, 
                # If rm command is executed, permission denied error occurs, so execute chmod 777.
                print(f"sudo chmod -R 777 {path}");
                chamodResult = os.system(f"sudo chmod -R 777 {path}");
                if chamodResult != 0 :
                    print(f"FAILED: Chmod failed {path}");
                    exit();

            # rm -rf repo
            print(f"rm -rf {path}");
            deleteResult = os.system(f"rm -rf {path}");
            if deleteResult != 0 :
                print(f"FAILED: Delete repo is failed {path}");
                exit();
            print(f"Delete repo is success {path}");

        # change dir
        cloneDirPath = "vendor/mediatek/tv/packages/apps";
        print(f"cd {cloneDirPath}");
        os.chdir(cloneDirPath);

        # Clone repo
        cloneRepoList = [
            "https://www.dummy/sample1" + " sample1",
            "https://www.dummy/sample2" + " sample2",
            "https://www.dummy/sample3" + " sample3",
        ];
        for repo in cloneRepoList :
            # git clone repo
            print(f"git clone -b sample-test {repo}");
            cloneResult = os.system(f"git clone -b sample-test {repo}");
            if cloneResult != 0 :
                print(f"FAILED: Clone repo is failed {repo}");
                exit();
            print(f"Clone repo is success {repo}");

def main() :
    ReplaceRepo().execute();


main();