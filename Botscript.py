import requests, json
import pypd
from jira import JIRA

data = json.load(open('guru_response.json'))


def pagerduty_call():
    pypd.EventV2.create(data={
        'routing_key': '<pagerduty integration key>',
        'event_action': 'trigger',
        'payload': {
            'summary': 'This is an SLACK BOT Error Event!',
            'severity': 'error',
            'source': 'SLACK BOT',
        }
    })


def url_check(url, key, item, message):
    try:
        r = requests.get(url,timeout=3)
        r.raise_for_status()
        response_result = data[key][item]['response']
        return response_result
    except requests.exceptions.HTTPError as errh:
        pagerduty_call()
        print ("Http Error:", errh)
        return ("Sorry to hear that, looks like url is inaccessible. `pageryduty` has already been initiated, we will keep you posted. \n if you don't see any pagerduty creation notification in this channel then you can create one using */pd* to trigger pagerduty ")
    except requests.exceptions.ConnectionError as errc:
        pagerduty_call()
        print ("Error Connecting:", errc)
        return ("`Error Connecting:` Sorry to hear that, looks like url is inaccessible. `pageryduty` has already been initiated, we will keep you posted. \n if you don't see any pagerduty creation notification in this channel then you can create one using */pd* to trigger pagerduty ")
    except requests.exceptions.Timeout as errt:
        pagerduty_call()
        print ("Timeout Error:", errt)
        return ("`Timeout Error:` Sorry to hear that, looks like url is inaccessible. `pageryduty` has already been initiated, we will keep you posted. \n if you don't see any pagerduty creation notification in this channel then you can create one using */pd* to trigger pagerduty ")
    except requests.exceptions.RequestException as err:
        pagerduty_call()
        print ("oops: Something Else", err)
        return ("`oops unknown error encountered:` Sorry to hear that, looks like url is inaccessible. `pageryduty` has already been initiated, we will keep you posted. \n if you don't see any pagerduty creation notification in this channel then you can create one using */pd* to trigger pagerduty ")


def wiki_url(url, key, item, message):
    try:
        if not url:
            raise ValueError('empty string')
        else:
            return url
    except ValueError as e:
        return("oops: got empty response for wiki link",e)

def create_issue_jira(url, key, item, message):
    new_issue_dict = {
        'project': {'key': '<Your Project>'},
        'summary': "Request for Creating New Jira Ticket via Slackbot)",
        'description': message,
        'assignee': {'name': '<assignee>'},
        'issuetype': {'name': 'Story'},
        'components': [{'name': '<comp>'}]
    }
    Jira_SA_Username = "<Jira service account user name>"
    Jira_SA_Password = "<Jira service account password>"
    try:
        jira = JIRA(basic_auth=(Jira_SA_Username,Jira_SA_Password),server="<Jira Url>")
        #issue = jira.create_issue(project=project, summary=summary, description=message, issuetype={'name':issuetype}, assignee={'name': assignee}, components=[{"name":components}], customfield_12006=customfield_12006)
        issue = jira.create_issue(fields=new_issue_dict)
        url["attachments"][0]["title"] = '<Jira Url>/jira/browse/%s' % issue.key
        return url
    except Exception as e:
        error = "`Unable to create JIRA, Encountered Error`"
        return json.dumps({'success': False, 'output': error})
