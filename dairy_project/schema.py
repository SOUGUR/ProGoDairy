import strawberry
from suppliers.schema import Query as SupplierQuery, Mutation as SupplierMutation
from distribution.schema import Query as DistributionQuery, Mutation as DistributionMutation

@strawberry.type
class Query(SupplierQuery, DistributionQuery):
    pass

@strawberry.type
class Mutation(SupplierMutation, DistributionMutation):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)

