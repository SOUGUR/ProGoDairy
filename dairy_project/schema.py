import strawberry
from suppliers.schema import Query as SupplierQuery, Mutation as SupplierMutation
from distribution.schema import Query as DistributionQuery, Mutation as DistributionMutation
from collection_center.schema import Query as CollectionCenterQuery, Mutation as CollectionCenterMutation
from plants.schema import Query as PlantsQuery
from milk.schema import Mutation as MilkSampleMutation, Query as MilkSampleQuery
from accounts.schema import Query as AccountsQuery, Mutation as AccountsMutation
from notifications.schema import Query as NotificationQuery, Mutation as NotificationMutation

@strawberry.type
class Query(SupplierQuery, DistributionQuery, CollectionCenterQuery, PlantsQuery, MilkSampleQuery, AccountsQuery, NotificationQuery):
    pass

@strawberry.type
class Mutation(SupplierMutation, DistributionMutation, CollectionCenterMutation, MilkSampleMutation, AccountsMutation, NotificationMutation):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)

