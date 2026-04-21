class CustomAuthUser:
    def __init__(self, user_data):
        self.__dict__.update(user_data)
        self.is_authenticated = True

    def __str__(self):
        return f"CustomAuthUser({self.__dict__})" 