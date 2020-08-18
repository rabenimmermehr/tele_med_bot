CONTEXT_ARGS_TIME_INDEX = 0
CONTEXT_ARGS_TIMEZONE_INDEX = 1

# https://stackoverflow.com/questions/33848773/getattr-for-a-list-index-in-python
def getitem(container, i, default=None):
    """
    Returns ith item or default
    """
    try:
        return container[i]
    except IndexError:
        return default
