from enum import Enum

class UserRole(Enum):       # different User Roles (Premium User not used at the moment)
                            # idea is that Users can only subscribe free API's, Admins can subscribe premium API's too
    USER = "USER"
    ADMIN = "ADMIN"
    PREMIUM_USER = "PREMIUM_USER"

    def __str__(self):
        return self.name

class SubscriptionType(Enum):       # possible Subscription Types (at the moment not used)
                                    # idea is that some subscriptions can be subscribed for free, some are premium
    FREE = "FREE"
    PREMIUM = "PREMIUM"

    def __str__(self):
        return self.name

class ApiStatusMessages(Enum):      # status Messages the internal API's (Scheduler, Dataconnectors) return
    SUCCESS = "SUCCESS: "
    WARNING = "WARNING: "
    ERROR = "ERROR: "

    def __str__(self):
        return self.value

class SubscriptionStatus(Enum):     # possible Statuses a Subscription can have
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ERROR = "ERROR"

    def __str__(self):
        return self.name

class Permissions(Enum):
    # InfluxDB permissions
    INFLUX_GET_DATA = "influxGetData"

    # PostgreSQL permissions
    AVAILABLE_APIS = "availableApis"
    SUBSCRIPTIONS = "subscriptions"
    SUBSCRIPTIONS_BY_USER_ID = "subscriptionsByUserID"

    # Scheduler API permissions
    SUBSCRIBE_API = "subscribeApi"
    RESUBSCRIBE_API = "resubscribeApi"
    UNSUBSCRIBE_API = "unsubscribeApi"


    def __str__(self):
        return self.value