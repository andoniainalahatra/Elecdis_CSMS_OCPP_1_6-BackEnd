class Subscription_data:
    id: int
    type_subscription: str

def get_subscription_data(subscription):
    return Subscription_data(
        id=subscription.id,
        type_subscription=subscription.type_subscription
    )

def get_list_subscription_data(subscriptions):
    return [Subscription_data(
        id=subscription.id,
        type_subscription=subscription.type_subscription
    ) for subscription in subscriptions]