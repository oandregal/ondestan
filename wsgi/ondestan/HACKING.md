How to add and localize new strings

    # introduce the new string to localize
    python setup.py extract_messages update_catalog -l es
    # edit po file
    python setup.py compile_catalog
