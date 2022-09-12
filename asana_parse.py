from datetime import datetime
from typing import List, TypedDict
import asana
from asana.resources.projects import Projects
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--trello-key", dest="trello_key", help="Trello Oauth API Key", required=True)
parser.add_argument("--trello-secret", dest="trello_secret", help="Trello Oauth API Token/Secret", required=True)
parser.add_argument("--asana-pat", dest="asana_pat", help="Asana API Personal Access Token", required=True)
parser.add_argument("--board", dest="board", help="Board name that you want to move from Asana to Trello", required=True)
args = parser.parse_args()

KEY = args.trello_key
TOKEN = args.trello_secret
PAT = args.asana_pat
BOARD = args.board

class Subtask:
    ATTR_LIST = ["name", "comments", "subtasks", "done", "description", "parent", "column", "is_separator"]
    name: str
    comments: List[str]
    done: bool
    description: str
    parent: str
    column: str
    is_separator: bool

    def __str__(self):
        string = ['{}="{}"'.format(i, getattr(self, i)) for i in self.ATTR_LIST]
        return '"' + ", ".join(string) + '"'

    def __init__(self, **kwargs):
        for i in self.ATTR_LIST:
            if i in kwargs:
                setattr(self, i, kwargs[i])

    def to_json(self):
        dic = {}
        for attr in self.ATTR_LIST:
            if getattr(self, attr):
                if attr == "subtasks":
                    dic[attr] = [i.to_json() for i in getattr(self, attr)] 
                    continue
                dic[attr] = getattr(self, attr)
        return dic

    def from_json(self, json: dict[str, any]):
        for key, value in json.items():
            if key not in self.ATTR_LIST:
                raise ValueError(f"Key {key} not found in Attribute List")
            if key == "subtasks":
                    self.subtasks = [Subtask().from_json(i) for i in value] 
                    continue
            setattr(self, key, value)
        return self

class MetaTask(Subtask):
    subtasks: List[Subtask]

    def __str__(self):
        string = ['{}="{}"'.format(i, getattr(self, i)) for i in self.ATTR_LIST]
        return '"' + ", ".join(string) + '"'

class Task(TypedDict):
    gid: str
    assignee: dict
    assignee_status: str
    completed: bool
    completed_at: datetime
    created_at: str
    due_at: datetime
    due_on: datetime
    followers: list
    hearted: bool
    hearts: list
    is_rendered_as_separator: bool
    liked: bool
    likes: list
    memberships: list
    modified_at: str
    name: str
    notes: str
    num_hearts: int
    num_likes: int
    parent: dict
    permalink_url: str
    projects: list
    resource_type: str
    start_at: datetime
    start_on: datetime
    subtasks: list
    tags: list
    resource_subtype: str
    workspace: dict

def get_metatasks():
    client = asana.Client.access_token(PAT)
    me = client.users.me()

    workspace_id = me['workspaces'][0]['gid']
    projects = client.projects.get_projects_for_workspace(workspace_id)
    board_id = [i['gid'] for i in projects if i['name'] == BOARD][0]
    fields = ["is_rendered_as_separator", "subtasks", "resource_subtype", "name", "memberships", "memberships.section", "memberships.section.name", "parent", "parent.name", "completed", "notes",
        "subtasks.is_rendered_as_separator", "subtasks.subtasks", "subtasks.resource_subtype", "subtasks.name", "subtasks.memberships", "subtasks.memberships.section", 
        "subtasks.memberships.section.name", "subtasks.parent", "subtasks.parent.name" "subtasks.completed", "subtasks.notes"
    ]
    tasks: list[Task] = client.tasks.get_tasks(params={'project': board_id}, opt_fields=fields)

    def create_metatask_from_asana(task: Task):
        #print(task)
        metatask = MetaTask()
        metatask.name = task['name']
        metatask.description = task['notes'] if task.get('notes') else ""
        metatask.done = task['completed']
        metatask.column = [i['section']['name'] for i in task['memberships']][0] if task.get('memberships') else []
        metatask.parent = task['parent']['name'] if task.get('parent') else task['memberships'][0]['section']['name']
        # Comments are called stories in Asana
        stories = client.stories.get_stories_for_task(task['gid'])
        metatask.comments = [story['text'] for story in stories if 'comment' in story['resource_subtype']]
        metatask.is_separator = task["is_rendered_as_separator"] if 'is_rendered_as_separator' in task else False
        metatask.subtasks = [create_metatask_from_asana(client.tasks.get_task(i['gid'], opt_fields=fields)) for i in client.tasks.get_subtasks_for_task(task['gid'])]
        return metatask

    meta_list: List[MetaTask] = [create_metatask_from_asana(i) for i in tasks]
    #meta_list: List[MetaTask] = [create_metatask_from_asana(client.tasks.get_task(i['gid'])) for i in tasks]

    return meta_list

if __name__ == "__main__":
    data = get_metatasks()
    print([str(i) for i in data])
