


class Service:
    def __init__(self, name, secret_key):
        self.name = name
        self.secret_key = secret_key
    def get_name(self):
        return self.name

    def get_secret_key(self):
        return self.secret_key
        