from tortoise import fields, models


class User(models.Model):
    id = fields.UUIDField(pk=True)
    admin = fields.BooleanField()

    name = fields.CharField(max_length=255)
    surname = fields.CharField(max_length=255)
    bio = fields.CharField(max_length=255)

    email = fields.CharField(max_length=255)
    password_hash = fields.CharField(max_length=255)


class Notification(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User")
    message = fields.CharField(max_length=255)


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


class Comment(models.Model):
    id = fields.IntField(pk=True)
    banned = fields.BooleanField(default=False)
    commenter = fields.ForeignKeyField("models.User")
    book = fields.ForeignKeyField("models.Book")

    stars = fields.IntField()
    message = fields.CharField(max_length=512)
    created_at = fields.DatetimeField(auto_now_add=True)


class Feedback(models.Model):
    id = fields.IntField(pk=True)

    title = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255)
    issue_type = fields.IntField()
    message = fields.CharField(max_length=255)

    @staticmethod
    def issue_index(s: str):
        return {
            "-": 0,
            "new_publisher": 1,
            "new_book": 2,
            "fix_bug": 3,
            "fix_typo": 4,
        }[s]


class DownloadSource(models.Model):
    id = fields.IntField(pk=True)

    filetype = fields.CharField(max_length=10)
    url = fields.CharField(max_length=128)
    book = fields.ForeignKeyField("models.Book")


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
