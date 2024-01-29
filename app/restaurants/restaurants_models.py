from tortoise import fields
from tortoise.models import Model
class Restaurant(Model):
    work_time_start = fields.DatetimeField()
    work_time_stop = fields.DatetimeField()
    adress = fields.CharField(max_length=255, unique=True, null=False)
    order_delivery = fields.BooleanField()
    order_pickup = fields.BooleanField()
    order_inside = fields.BooleanField()
    is_working = fields.BooleanField() #?
    #delivery_area = fields. ???
    city = fields.CharField(max_length=255, null=False)
    min_sum = fields.IntField()
    timezone=fields.CharField(max_length=255)