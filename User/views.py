import json
from django.http import HttpRequest, HttpResponse

def check_for_board_data(body):
    board = require(body, "board", "string", err_msg="Missing or error type of [board]")
    
    # TODO Start: [Student] add checks for type of boardName and userName
    board_name = ""
    user_name = ""
    board_name = require(body, "boardName", "string", err_msg="Missing or error type of [boardName]")
    user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
    # TODO End: [Student] add checks for type of boardName and userName
    
    assert 0 < len(board_name) <= 50, "Bad length of [boardName]"
    
    # TODO Start: [Student] add checks for length of userName and board
    assert 0 < len(user_name) <=50, "Bad length of [userName]"
    assert len(board) == 2500, "Bad length of [board]"
    # TODO End: [Student] add checks for length of userName and board
    
    
    # TODO Start: [Student] and more checks (you should read API docs carefully)
    is_zero_or_one = True
    for i in range(2500):
        if board[i] != "0" and board[i] != "1":
            is_zero_or_one = False
            break
    assert is_zero_or_one == True, "Invalid char in [board]"
    # TODO End: [Student] and more checks (you should read API docs carefully)
    
    return board, board_name, user_name

# Create your views here.
def startup(req: HttpRequest):
    return HttpResponse("Congratulations! You have successfully installed the requirements. Go ahead!")

def login_normal(req: HttpRequest):
    return HttpResponse("login_normal")