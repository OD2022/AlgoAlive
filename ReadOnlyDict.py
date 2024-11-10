class ReadOnlyDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        if key not in self:
            super().__setitem__(key, value)

    def update(self, *args, **kwargs):
        for key, value in args[0].items():
            if key not in self:
                super().__setitem__(key, value)

    def __delitem__(self, key):
        # Ignore deletion
        return