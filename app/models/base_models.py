from tortoise import fields, models


class UUIDDBModel(models.Model):
    """Base model with uuid primary key"""

    id = fields.UUIDField(pk=True, index=True)
    is_deleted = fields.BooleanField(default=False)

    class Meta:
        abstract = True


class IdDBModel(models.Model):
    """Base model with integer id primary key"""

    id = fields.BigIntField(pk=True, index=True)
    is_deleted = fields.BooleanField(default=False)

    class Meta:
        abstract = True
