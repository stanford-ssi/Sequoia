import asyncio, os
import google_sheets
import github_issues

#-----------------------------------------------------------
# Download Google Sheet and Parse into JSON
#-----------------------------------------------------------

sequoia =  "1LgfZWeo7Q2KEg5C1LhN5yxGT8s4gFGmod-ak6bNA-iM"
sheet_and_range = "Requirements_Working!B2:G"

sheet = google_sheets.GoogleSheet(sequoia, sheet_and_range)
sheet.json_from_rows(0, "google_issues.json")

#-----------------------------------------------------------
# Parse JSON into GitHub style issues and put on appropriate 
# repositories
#-----------------------------------------------------------

title_format = [
    ("column", "Tag"),
    ("text", " - "),
    ("column", "Requirement")
]

body_format = [
    ("column", "Description")
]

label_list = [
    ("column", "Team"), 
    ("column", "Subsystem"), 
    ("text", "requirement"),
    ("column", "Tag")
]

repo_location = "Team"
repo_prefix = "sequoia"

issue_dict = github_issues.parse_json_issues("google_issues.json", title_format, body_format, label_list, by_repo=True, repo_location=repo_location, repo_prefix=repo_prefix)
asyncio.run(github_issues.sync_across_repos("polygnomial", issue_dict))

os.system("rm google_issues.json")