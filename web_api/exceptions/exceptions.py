""" Custom exceptions """


class UserIsExistError(Exception):
    """ Exception for not unique username error """
    message = "This user is already exist!"

    def __init__(self, error_code=None):
        super().__init__(self.message)
        self.error_code = error_code


class UserEmailExistError(Exception):
    """ Exception for not unique email error """
    message = "User with this email already exist!"

    def __init__(self, error_code=None):
        super().__init__(self.message)
        self.error_code = error_code


class ElasticError(Exception):
    """ Exception for elastic errors """
    message = "Error occured with elastic search!"

    def __init__(self, error_code=None):
        super().__init__(self.message)
        self.error_code = error_code
