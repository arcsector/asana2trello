import json
from turtle import write
from typing import Tuple, TypedDict
from trello import TrelloClient, Board, List, Card
from asana_parse import MetaTask, get_metatasks, KEY, TOKEN, BOARD
from pprint import pprint
import logging

logging.basicConfig(level=logging.ERROR)

client = TrelloClient(
    api_key=KEY,
    api_secret=TOKEN,
)

def write_to_file(filename: str, metatasks: list[MetaTask]):
    jsonified_data = [i.to_json() for i in metatasks]
    json.dump(jsonified_data, open(filename, 'w+'), indent=2, sort_keys=True)

def read_from_file(filename: str) -> list[MetaTask]:
    jsonified_data = json.load(open(filename, 'r'))
    metatasks = [MetaTask().from_json(i) for i in jsonified_data]
    return metatasks

class SortedTasks(TypedDict):
    column: str
    tasks: list[MetaTask]

class HeirarchyTasks(TypedDict):
    title: str
    subtasks: list[Tuple]

def close_duplicate_lists(mylists: list[List], client: TrelloClient):
    dummy_board = client.add_board("dummy_board")
    for list in mylists:
        count = 0
        for i in mylists:
            if i.name == list.name:
                count += 1
        if count > 1:
            logging.info(f"closing list {list.name}")
            list.move_to_board(dummy_board)
    dummy_board.close()

def add_missing_columns(tasks: list[MetaTask], board: Board):
    # Get columns
    board.fetch()
    lists = board.list_lists()
    for asana_task in tasks:
        # Get column names
        logging.debug(f"Processing task \"{asana_task.name}\"")
        trello_column_names = [i.name for i in lists]
        # if it's not there, add it
        if hasattr(asana_task, "column"):
            if asana_task.column not in trello_column_names:
                logging.info(f"Adding \"{asana_task.column}\" to list \"{str(trello_column_names)}\"")
                board.add_list(asana_task.column)
                board.fetch()
                lists = board.list_lists()

    # return all columns
    return board.list_lists()

def add_subtask_to_card(subtasks: list[MetaTask], card: Card):
    title = "Task List"
    current_keys_list = [title]
    
    # Create multiple checklists from subtask separators using separator 
    heirarchy_subtasks: list[HeirarchyTasks] = [{"title": title, "subtasks": []}]
    for task in subtasks:
        # Test if this is the header
        if hasattr(task, "is_separator"):
            if task.is_separator:
                logging.info(f"adding parsed header \"{task.name}\"")
                title = task.name
                current_keys_list.append(title)
                heirarchy_subtasks.append({"title": title, "subtasks": []})
                continue
        logging.info(f"parsing subtask task \"{task.name}\" for \"{title}\"")
        [j for j in heirarchy_subtasks if j["title"] == title][0]["subtasks"].append(
            (task.name, task.done if hasattr(task, "done") else False)
        )

    # start processing subtasks
    for column_task in heirarchy_subtasks:
        logging.info(f"Adding checklist \"{column_task['title']}\"")
        logging.info(f"Checklist subtasks: \"{column_task['subtasks']}\"")
        card.add_checklist(
            title=column_task["title"], 
            items = [i[0] for i in column_task["subtasks"]], 
            itemstates = [i[1] for i in column_task["subtasks"]]
        )

def add_cards_to_list(tasks: list[MetaTask], trello_list: List):
    list_cards = trello_list.list_cards(card_filter="")
    for asana_task in tasks:
        if asana_task.name in [i.name for i in list_cards]:
            logging.info(f"The task \"{asana_task.name}\" already exists in list {trello_list.name} - skipping")
            continue
        logging.info(f"Adding card \"{asana_task.name}\" to list \"{trello_list.name}\"")
        card = trello_list.add_card(name=asana_task.name)
        if hasattr(asana_task, "description"):
            card.set_description(asana_task.description)
        if hasattr(asana_task, "comments"):
            for comment in asana_task.comments:
                card.comment(comment)
        if hasattr(asana_task, "subtasks"):
            add_subtask_to_card(asana_task.subtasks, card)
        if hasattr(asana_task, "done"):
            card.set_closed(closed=True) if asana_task.done else None

all_boards = client.list_boards()
if BOARD not in [i.name for i in all_boards]:
    my_board = client.add_board(BOARD)
else:
    my_board = [i for i in all_boards if i.name == BOARD][0]
board_list_names = [i.name for i in my_board.list_lists()]

if len(board_list_names) > len(set(board_list_names)):
    close_duplicate_lists(my_board.list_lists(), client)

asana_tasks = get_metatasks()

board_lists = add_missing_columns(asana_tasks, my_board)

sorted_tasks: list[SortedTasks] = []
current_keys_list = []
for i in asana_tasks:
    # test if our column is sorted correctly
    if i.column not in current_keys_list:
        logging.info(f"creating sorted column \"{i.column}\"")
        current_keys_list.append(i.column)
        sorted_tasks.append({"column": i.column, "tasks": [i]})
        continue
    logging.debug(f"adding sorted task \"{i.name}\"")
    [j for j in sorted_tasks if j["column"] == i.column][0]["tasks"].append(i)

for grouping in sorted_tasks:
    board_lists = my_board.list_lists()
    trello_list = [i for i in board_lists if i.name == grouping["column"]][0]
    logging.info(f"Adding all cards to list \"{trello_list.name}\"")
    add_cards_to_list(grouping['tasks'], trello_list)
