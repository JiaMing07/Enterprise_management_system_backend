from utils.utils_require import require
 

def get_args(body, args, types,  **default_args):
    ret = []
    if len(types) < len(args):
        while len(types) < len(args):
            types.append("string")
    for i in range(len(args)):
        err_message = "Missing or or error type of [{}]".format(args[i])
        value = require(body, args[i], type = types[i], err_msg=err_message) 
        ret.append(value)

    return ret

