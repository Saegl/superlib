from tortoise import fields, models


class User(models.Model):
    id = fields.UUIDField(pk=True)

    name = fields.CharField(max_length=255)
    surname = fields.CharField(max_length=255)
    bio = fields.CharField(max_length=255)

    email = fields.CharField(max_length=255)
    password_hash = fields.CharField(max_length=255)


class Author(models.Model):
    id = fields.IntField(pk=True)

    name = fields.CharField(max_length=255)
    surname = fields.CharField(max_length=255)
    bio = fields.CharField(max_length=255)


class Publisher(models.Model):
    id = fields.IntField(pk=True)

    name = fields.CharField(max_length=255)


class Category(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)


class Book(models.Model):
    isbn = fields.CharField(pk=True, max_length=255)

    author = fields.ForeignKeyField("models.Author")
    title = fields.CharField(max_length=255)
    description = fields.CharField(max_length=512)
    category = fields.ForeignKeyField("models.Category")
    image_url = fields.CharField(max_length=255)
    publisher = fields.ForeignKeyField("models.Publisher")
    year = fields.IntField()
    pages = fields.IntField()

    created_at = fields.DatetimeField(auto_now_add=True)
    views = fields.IntField()
