class UserIsExistError(Exception):
    message = "This user is already exist"

    def __init__(self, error_code=None):
        super().__init__(self.message)
        self.error_code = error_code

class UserEmailExistError(Exception):
    message = "User with this email already exist"

    def __init__(self, error_code=None):
        super().__init__(self.message)
        self.error_code = error_code
