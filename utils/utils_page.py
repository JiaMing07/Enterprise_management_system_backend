from Asset.models import *
from User.models import *

def page_list(all_list, page, length):
    return_list = []
    if length % 20 != 0:
        if page == int(length/20) + 1:
            for i in range(length - (page-1)*20):
                return_list.append(all_list[(int(page)-1)*20+i])
        else:
            for i in range(20):
                return_list.append(all_list[(int(page)-1)*20+i])
    else:
        for i in range(20):
            return_list.append(all_list[(int(page)-1)*20+i])
    return return_list