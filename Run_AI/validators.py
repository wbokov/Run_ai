def check_weight(weight):
    try:
        weight = float(weight)
        if weight <= 20 or weight >= 250:
            raise Exception
    except:
        return True
    return False


def check_age(age):
    try:
        age = int(age)
        if age <= 1 or age >= 150:
            raise Exception
    except:
        return True
    return False


def check_times(times):
    try:
        times = int(times)
        if times > 7 or times < 1:
            raise Exception
    except:
        return True
    return False
