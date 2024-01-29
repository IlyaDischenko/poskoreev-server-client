from tortoise import fields
from tortoise.models import Model
class Product(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255, null=False)
    description = fields.CharField(max_length=255)
    img= fields.CharField(max_length=255)

class ProductType:
    id = fields.IntField(pk=True)
    type = fields.CharField(max_length=255)