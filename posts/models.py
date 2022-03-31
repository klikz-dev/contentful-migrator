from django.db import models
from ckeditor.fields import RichTextField


class Category(models.Model):
    slug = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=200, null=False, blank=False)
    description = models.CharField(max_length=2000, null=False, blank=False)

    def __str__(self):
        return self.name


class Tag(models.Model):
    slug = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=200, null=False, blank=False)
    description = models.CharField(max_length=2000, null=False, blank=False)

    def __str__(self):
        return self.name


class Author(models.Model):
    slug = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=200, null=False, blank=False)
    description = models.CharField(max_length=2000, null=False, blank=False)
    avatar = models.URLField(
        max_length=200, default='', blank=True, null=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    slug = models.CharField(max_length=200, primary_key=True)
    old_link = models.URLField(
        max_length=200, default='', blank=True, null=True)

    title = models.CharField(
        max_length=200, default='', blank=False, null=False)
    content = RichTextField(default="")
    excerpt = RichTextField(default="")

    date = models.DateTimeField(blank=False, null=False)

    author = models.ForeignKey(
        Author, related_name='posts', default=None, blank=True, null=True, on_delete=models.CASCADE)

    categories = models.ManyToManyField(
        Category, related_name='posts', default=None, blank=True)
    tags = models.ManyToManyField(
        Tag, related_name='posts', default=None, blank=True)


IMAGETYPE_OPTIONS = (
    ('thumbnail', 'Thumbnail'),
    ('attachment', 'Attachment'),
)


class Image(models.Model):
    slug = models.CharField(max_length=200, primary_key=True)
    link = models.URLField(
        max_length=200, default='', blank=False, null=False)
    alt = models.CharField(max_length=200, null=True, blank=True)

    post = models.ForeignKey(
        Post, related_name='images', default=None, blank=True, null=True, on_delete=models.CASCADE)

    type = models.CharField(
        max_length=20, default='attachment', choices=IMAGETYPE_OPTIONS, null=False, blank=False)

    def __str__(self):
        return self.slug
