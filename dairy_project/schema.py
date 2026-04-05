import strawberry

from accounts.schema import Mutation as AccountsMutation
from accounts.schema import Query as AccountsQuery
from collection_center.schema import Mutation as CollectionCenterMutation
from collection_center.schema import Query as CollectionCenterQuery
from distribution.schema import Mutation as DistributionMutation
from distribution.schema import Query as DistributionQuery
from milk.schema import Mutation as MilkSampleMutation
from milk.schema import Query as MilkSampleQuery
from plants.schema import Mutation as PlantsMutation
from plants.schema import Query as PlantsQuery
from suppliers.schema import Mutation as SupplierMutation
from suppliers.schema import Query as SupplierQuery


@strawberry.type
class Query(SupplierQuery, DistributionQuery, CollectionCenterQuery, PlantsQuery, MilkSampleQuery, AccountsQuery):
    pass

@strawberry.type
class Mutation(SupplierMutation, DistributionMutation, PlantsMutation, CollectionCenterMutation, MilkSampleMutation, AccountsMutation):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)

