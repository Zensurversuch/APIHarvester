from enum import Enum

class UserRole(Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    PREMIUM_USER = "PREMIUM_USER"

    def __str__(self):
        return self.name

class SubscriptionType(Enum):
    FREE = "FREE"
    PREMIUM = "PREMIUM"

    def __str__(self):
        return self.name
    

class ApiStatusMessages(Enum):
    SUCCESS = "SUCCESS: "
    WARNING = "WARNING: "
    ERROR = "ERROR: "

    def __str__(self):
        return self.value

class SubscriptionStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ERROR = "ERROR"

    def __str__(self):
        return self.name
    