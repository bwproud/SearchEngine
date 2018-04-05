# Accepts two sorted posting lists and merges them into one sorted list using OR logic
def or_merge(l1, l2):
    if l1 == None and l2 == None:
        return []
    elif l1 == None:
        return l2
    elif l2 == None:
        return l1

    i = 0    
    j = 0

    res = []
    while i < len(l1) and j < len(l2):
        p1 = l1[i]
        p2 = l2[j]

        if p1 == p2:
            res.append(p1)
            i += 1
            j += 1
        elif p1 < p2: 
            # Found unique in p1
            res.append(p1)
            i += 1
        else:
            # Found unique in p2
            res.append(p2)
            j += 1

    # Add all remaining from the longer list
    while i < len(l1):
        res.append(l1[i])
        i += 1

    while j < len(l2):
        res.append(l2[j])
        j += 1

    return res

def positional_and(l1, l2):
    """
        Given two sorted lists of postitions within one file, return all locations
        in l2 where the l1 contains the previous position
    """
    if l1 == None or l2 == None:
        return []

    i = 0
    j = 0

    res = []
    while i < len(l1) and j < len(l2):
        p1 = l1[i]+1
        p2 = l2[j]
        if p1 == p2:
            res.append(p2)
            i += 1
            j += 1
        elif p1 < p2:
            i += 1
        else:
            j += 1

    return res