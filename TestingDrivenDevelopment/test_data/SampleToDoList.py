class SampleToDoList:
    items_list = [
        "Buy peacock feather",
        "Use peacock feather to make a bite"
    ]

    @classmethod
    def get_items_list(cls):
        return cls.items_list
