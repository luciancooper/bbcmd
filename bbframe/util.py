


class BBFrameError(Exception):
    pass


def scolDec(col,place=3,align="<"):
    f = '{:.%if}'%place
    s = [f.format(x) for x in col]
    a = '{:%s%i}'%(align,max(len(x) for x in s))
    return [a.format(x) for x in s]

def scolInt(col,align="<"):
    s = [str(x) for x in col]
    a = '{:%s%i}'%(align,max(len(x) for x in s))
    return [a.format(x) for x in s]
