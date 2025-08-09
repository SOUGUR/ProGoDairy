import strawberry
from suppliers.schema import Query as SupplierQuery, Mutation as SupplierMutation
from distribution.schema import Query as DistributionQuery, Mutation as DistributionMutation
from collection_center.schema import Query as CollectionCenterQuery, Mutation as CollectionCenterMutation
from plants.schema import Query as PlantsQuery

@strawberry.type
class Query(SupplierQuery, DistributionQuery, CollectionCenterQuery, PlantsQuery):
    pass

@strawberry.type
class Mutation(SupplierMutation, DistributionMutation, CollectionCenterMutation):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)

