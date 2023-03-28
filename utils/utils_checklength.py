def checklength(string, lowerbound, upperbound, name):
    assert lowerbound < len(string) <=upperbound, "Bad length of [{}]".format(name)