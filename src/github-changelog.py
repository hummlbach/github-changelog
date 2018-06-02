#!/usr/bin/python3

import requests
import sys
import operator

apiUrl = "https://api.github.com/"

credentials = ("github-username", "password")

user = sys.argv[1]
date = sys.argv[2]

def pageCount(request):
    response = requests.get(apiUrl+request, auth=credentials)
    lastPage = 1
    try:
        lastPage = response.headers["Link"].split("=")[3].split(">")[0]
    except:
        return 1
    return int(lastPage)


def reposByUser(user):
    repoPageCount = pageCount("users/"+user+"/repos")
    repoNames = []
    for page in range(1, repoPageCount+1):
        response = requests.get(apiUrl+"users/"+user+"/repos?page="+str(page), auth=credentials)
        repoList = response.json()
        repoNames += [repo["full_name"] for repo in repoList]
    return repoNames

# would be nice to have this as a class, where
# - the returned json object would be encapsulated
# - issuesModifiedSince would be a constructor
# - changelog would act as a toString method
# - filter would be a method modifying the issue list

def issuesModifiedSince(repoName, date):
    datetime = date+"T00:00:01Z"
    commitPageCount = pageCount("repos/"+repoName+"/issues?state=closed&since="+datetime)
    issueList = []
    for page in range(1, commitPageCount+1):
        response = requests.get(apiUrl+"repos/"+repoName+"/issues?state=closed&since="+datetime+"&page="+str(page), auth=credentials)
        issueList += response.json()
    return issueList


def changelog(issueList):
    for issue in issueList:
        print(" "+issue["title"]+"\n")
        print(" "+issue["html_url"]+"\n")
        print("----\n")

def filterIssueList(issueList, field, comparator, comparand):
    containsNot = lambda x, y: not operator.contains(x,y)
    ops = {'>': operator.gt,
           '<': operator.lt,
           '>=': operator.ge,
           '<=': operator.le,
           '=': operator.eq,
           '!in': containsNot,
           'in': operator.contains}
    return [issue for issue in issueList if ops[comparator](issue[field], comparand)]

print("Changes from "+user+" since "+date+" in repository...\n\n")
repoList = reposByUser(user)
for repoName in repoList:
    issueList = issuesModifiedSince(repoName, date)
    issueList = filterIssueList(issueList, "closed_at", ">=", date)
    issueList = filterIssueList(issueList, "title", "!in", "Weblate")
    if issueList:
        print("\n... "+repoName+":\n\n----\n")
        changelog(issueList)

