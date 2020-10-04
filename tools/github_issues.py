import os
import json
import github

class GitHubIssueSet:

    f = open("github_credentials.json", "r")
    token = json.load(f)["token"]
    g = github.Github(token)
    del token
    f.close()

    def __init__(self, filename, by_repo=False, repo_prefix=""):
        
            with open(filename, "r") as gs:
                # json containing issues synced from google sheet
                gs_issues = json.load(gs)

                gh_issues = {}

                # google sheet issues -> github style issues (with relevant naming), with Tags as keys
                for gs_issue in gs_issues:
                    gs_issue = gs_issues[gs_issue]
                    gh_issue = {}
                    gh_issue["title"] = f"{gs_issue['Tag']} - {gs_issue['Requirement']}"
                    gh_issue["body"] = gs_issue["Description"]

                    # get rid of repeated labels (in the case that team is the same as subsystem)
                    labels = [gs_issue["Team"], gs_issue["Subsystem"], "requirement", gs_issue['Tag']]
                    gh_issue["labels"] = list(frozenset(labels))

                    # sort everything issues by repository
                    if by_repo:
                        repo_suffix = gs_issue["Team"]
                        repo_name = f"{repo_prefix}-{repo_suffix}"

                        if repo_name not in gh_issues:
                            gh_issues[repo_name] = {}

                        gh_issues[repo_name][gs_issue['Tag']] = gh_issue

                    else:
                        gh_issues[gs_issue['Tag']] = gh_issue

            # store the github style issues        
            self.issues = gh_issues


    def sync_local_to_github(self, user, repo, issues=None):

        if issues == None:
            issues = self.issues
        
        repo = self.g.get_repo(f"{user}/{repo}")
        remote_issues_list = repo.get_issues(state='all')
        remote_issues = {}
        
        # create a dictionary of the issues on github for easier searching, with Tags as keys
        for gh_issue in remote_issues_list:
            gh_issue_dict = {}
            gh_issue_dict["labels"] = [ gh_issue.labels[i].name for i in range(len(gh_issue.labels)) ]

            # if "requirement" is not a label, do not add it to the dictionary
            if "requirement" not in frozenset(gh_issue_dict["labels"]):
                continue

            gh_issue_dict["title"] = gh_issue.title
            gh_issue_dict["body"] = gh_issue.body
            gh_issue_dict["issue"] = gh_issue

            # recover the issue's Tag
            index = gh_issue.title.find("-")
            tag = gh_issue.title[:index - 1]

            # here is where the issues would be deleted (if they have been removed from the spreadsheet)

            remote_issues[tag] = gh_issue_dict

        for issue in issues:

            # if the local Tag is not on GitHub (meaning the issue is not on GitHub), add it
            if issue not in remote_issues:
                print("title: ", issues[issue]["title"], "body: ", issues[issue]["body"], "labels: ", issues[issue]["labels"])
                # repo.create_issue(title=issues[issue]["title"], body=issues[issue]["body"], labels=['structures', 'requirement', 'ST1']) 
                repo.create_issue(title=issues[issue]["title"], body=issues[issue]["body"], labels=issues[issue]["labels"]) 

                # don't do anything else for this issue because it has just been added             
                continue
            
            # if the titles disagree (renamed on the google sheet), correct the title on GitHub
            if remote_issues[issue]["title"] != issues[issue]["title"]:
                remote_issues[issue]["issue"].edit(title=issues[issue]["title"])

            # if the bodies disagree (rewritten on the googlesheet), correct the title on GitHub
            if remote_issues[issue]["body"] != issues[issue]["body"]:
                remote_issues[issue]["issue"].edit(body=issues[issue]["body"])

            # if the labels disagree, reset the labels from the google sheet
            remote_labels = frozenset(remote_issues[issue]["labels"])
            local_labels = frozenset(issues[issue]["labels"])
            if remote_labels != local_labels:
                remote_issues[issue]["issue"].set_labels(*issues[issue]["labels"])

        del remote_issues


    def sync_across_repos(self, user):
        for repo in self.issues:
            self.sync_local_to_github(user, repo, self.issues[repo])
        


if __name__ == "__main__":
    issue_set = GitHubIssueSet("google_issues.json", by_repo=True, repo_prefix='sequoia')
    issue_set.sync_across_repos("polygnomial")