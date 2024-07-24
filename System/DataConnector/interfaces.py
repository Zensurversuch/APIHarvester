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