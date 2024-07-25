from enum import Enum

class UserRole(Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    PREMIUM_USER = "PREMIUM_USER"

    def __str__(self):
        return self.name

class SubscriptionType(Enum):
    FREE = "Free"
    PREMIUM = "Premium"

    def __str__(self):
        return self.name
    

class ApiStatusMessages(Enum):
    SUCCESS = "SUCCESS: "
    WARNING = "WARNING: "
    ERROR = "ERORR: "

    def __str__(self):
        return self.value

class SubscriptionStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ERROR = "ERORR"

    def __str__(self):
        return self.name
    