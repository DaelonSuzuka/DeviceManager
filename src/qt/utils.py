def enable_children(thing):
    """ recursively walk the provided thing and enable all of its widget children """
    for i in range(thing.count()):
        if thing.itemAt(i).widget():
            thing.itemAt(i).widget().setEnabled(True)
        else:
            enable_children(thing.itemAt(i))


def disable_children(thing):
    """ recursively walk the provided thing and disable all of its widget children """
    for i in range(thing.count()):
        if thing.itemAt(i).widget():
            thing.itemAt(i).widget().setEnabled(False)
        else:
            disable_children(thing.itemAt(i))