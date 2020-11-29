import os
import json
import github
import asyncio

def parse_json_issues(filename, title_format, body_format, label_list, by_repo=False, repo_location=None, repo_prefix=""):
        
    with open(filename, "r") as json_issues:
        # json containing issues synced from google sheet
        gs_issues = json.load(json_issues)
        gh_issues = {}

        # google sheet issues -> github style issues (with relevant naming), with Tags as keys
        for gs_issue in gs_issues:
            gs_issue = gs_issues[gs_issue]
            gh_issue = {}
            
            title = ''
            body = ''
            labels = []

            for pair in title_format:
                element_type = pair[0]
                element = pair[1]
                if element_type == "column":
                    title += f"{gs_issue[element]}"
                else:
                    title += element

            for pair in body_format:
                element_type = pair[0]
                element = pair[1]
                if element_type == "column":
                    body += f"{gs_issue[element]}"
                else:
                    body += element

            for pair in label_list:
                element_type = pair[0]
                element = pair[1]
                if element_type == "column":
                    labels.append(f"{gs_issue[element]}")
                else:
                    labels.append(element)

            gh_issue["title"] = title
            gh_issue["body"] = body

            # get rid of repeated labels (in the case that team is the same as subsystem)
            gh_issue["labels"] = list(frozenset(labels))

            # sort issues by repository
            if by_repo:
                repo_suffix = gs_issue["Team"]
                repo_name = f"{repo_prefix}-{repo_suffix}"

                if repo_name not in gh_issues:
                    gh_issues[repo_name] = {}

                gh_issues[repo_name][gs_issue['Tag']] = gh_issue

            else:
                gh_issues[gs_issue['Tag']] = gh_issue

    return gh_issues


async def sync_local_to_github(user, repo, issues, github_credentials_file="github_credentials.json"):

    f = open(github_credentials_file, "r")
    token = json.load(f)["token"]
    g = github.Github(token)
    del token
    f.close()
    
    repo = g.get_repo(f"{user}/{repo}")
    remote_issues_list = repo.get_issues(state='all')
    remote_issues = {}
    
    # create a dictionary of the issues on github for easier searching, with Tags as keys
    for gh_issue in remote_issues_list:
        gh_issue_dict = {}
        gh_issue_dict["labels"] = [ gh_issue.labels[i].name for i in range(len(gh_issue.labels)) ]

        # if "requirement" is not a label, do not add it to the dictionary
        # this will become necessary when issue deletion is implemented
        # if "requirement" not in frozenset(gh_issue_dict["labels"]):
        #    continue

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
            print(f"-------------------\nAdding issue on: {repo.name}\n Tag: {issue}\n Title: {issues[issue]['title']}\n Body: {issues[issue]['body']}\n Labels: {issues[issue]['labels']}\n-------------------\n")
            await _make_issue(repo, issues[issue])

            # don't do anything else for this issue because it has just been added             
            continue
        
        # if the titles disagree (renamed on the google sheet), correct the title on GitHub
        if remote_issues[issue]["title"] != issues[issue]["title"]:
            print(f"-------------------\nEditing issue on: {repo.name}\n Tag: {issue}\n >>> New Title: {issues[issue]['title']}\n <<< Old Title: {remote_issues[issue]['title']}\n Body: {issues[issue]['body']}\n Labels: {issues[issue]['labels']}\n-------------------\n")
            remote_issues[issue]["issue"].edit(title=issues[issue]["title"])

        # if the bodies disagree (rewritten on the googlesheet), correct the title on GitHub
        if remote_issues[issue]["body"] != issues[issue]["body"]:
            print(f"-------------------\nEditing issue on: {repo.name}\n Tag: {issue}\n Title: {issues[issue]['title']}\n >>> New Body: {issues[issue]['body']}\n <<< Old Body: {remote_issues[issue]['body']}\n Labels: {issues[issue]['labels']}\n-------------------\n")
            remote_issues[issue]["issue"].edit(body=issues[issue]["body"])

        # if the labels disagree, reset the labels from the google sheet
        remote_labels = frozenset(remote_issues[issue]["labels"])
        local_labels = frozenset(issues[issue]["labels"])
        if remote_labels != local_labels:
            print(f"-------------------\nEditing issue on: {repo.name}\n Tag: {issue}\n Title: {issues[issue]['title']}\n Body: {issues[issue]['body']}\n >>> New Labels: {issues[issue]['labels']}\n <<< Old Labels: {list(remote_labels)}\n-------------------\n")
            remote_issues[issue]["issue"].set_labels(*issues[issue]["labels"])

    del remote_issues


async def _make_issue(repo, issue):
    repo.create_issue(title=issue["title"], body=issue["body"], labels=issue["labels"])


async def sync_across_repos(user, issue_dict):
    for repo in issue_dict:
        await sync_local_to_github(user, repo, issue_dict[repo])