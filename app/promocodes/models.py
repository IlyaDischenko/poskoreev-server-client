from tortoise import fields
from tortoise.models import Model



class PromoCode(Model):
    id = fields.IntField(pk=True, auto_increment=True)
    short_name = fields.CharField(max_length=255, null=False)
    description = fields.CharField(max_length=255, null=True)
    # 1 - продукт, 2 - процент, 3 - рубли
    type = fields.IntField(default=2)
    count = fields.IntField(default=1, null=False)
    effect = fields.IntField(default=1, null=False)
    for_all = fields.BooleanField(default=False)
    start_day = fields.DatetimeField()
    end_day = fields.DatetimeField()
    min_sum = fields.IntField(null=True)
    #works_with = fields.ManyToManyField('models.ProductCategory')
    is_active = fields.BooleanField(default=True)

