from tortoise import fields, models


class User(models.Model):
    id = fields.UUIDField(pk=True)

    name = fields.CharField(max_length=255)
    surname = fields.CharField(max_length=255)
    bio = fields.CharField(max_length=255)

    email = fields.CharField(max_length=255)
    password_hash = fields.CharField(max_length=255)
