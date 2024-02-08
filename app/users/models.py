from tortoise import fields
from tortoise.models import Model
from datetime import datetime, timezone


class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, null=True)
    birthday = fields.DateField(null=True)
    email = fields.CharField(max_length=255, unique=True, null=True)
    number = fields.CharField(unique=True, null=False, max_length=255)
    code = fields.CharField(max_length=255)
    expires_at = fields.DatetimeField()
    telegram = fields.CharField(max_length=255, unique=True, null=True)
    promocodes = fields.ManyToManyField('models.PromoCodePercent')
    bonuses = fields.IntField(default=0, ge=0)

    async def get_all_promocodes(self):
        promocodes_set = await self.promocodes.filter(is_active=True)
        promocodes = []
        for i in promocodes_set:
            if i.end_day > datetime.now(timezone.utc):
                promocodes.append({'promocode': i.short_name,
                                   'description': i.description,
                                   'discount': i.discount,
                                   'min': i.min_sum,
                                   'expires_at': i.end_day.astimezone().strftime('%d.%m.%Y')})
        return promocodes


class UserJWT(Model):
    user = fields.ForeignKeyField('models.User', pk=True)
    refresh_code = fields.CharField(max_length=255)
    is_active = fields.BooleanField()

class UserBlacklist(Model):
    user_id = fields.IntField()