
def apt_out_parser(text):
    apps = text.strip().split("\n")
    result_set = []
    for app in apps:
        result_set.append({"name": app, "label_name": app})
    return result_set

def snap_out_parser(text):
    apps = text.strip().split("\n")
    result_set = []
    for app in apps:
        result_set.append({"name": app.split(" ")[0], "label_name": app.split(" ")[0]})
    result_set.pop(0)
    return result_set

def flatpak_out_parser(text):
    apps = text.strip().split("\n")
    result_set = []
    for app in apps:
        bbb = app.split("\t")
        try:
            result_set.append({"name": bbb[1], "label_name": bbb[0]})
        except:
            continue
    return result_set
