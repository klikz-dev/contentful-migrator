from django.db import models


class Author(models.Model):
    id = models.IntegerField(primary_key=True, null=False, blank=False)
    name = models.CharField(max_length=200, null=False, blank=False)
    slug = models.CharField(max_length=200, null=False, blank=False)
    description = models.CharField(max_length=2000, null=False, blank=False)

    def __str__(self):
        return str(self.id)


class Category(models.Model):
    id = models.IntegerField(primary_key=True, null=False, blank=False)
    name = models.CharField(max_length=200, null=False, blank=False)
    slug = models.CharField(max_length=200, null=False, blank=False)
    description = models.CharField(max_length=2000, null=False, blank=False)

    def __str__(self):
        return str(self.id)


class Tag(models.Model):
    id = models.IntegerField(primary_key=True, null=False, blank=False)
    name = models.CharField(max_length=200, null=False, blank=False)
    slug = models.CharField(max_length=200, null=False, blank=False)
    description = models.CharField(max_length=2000, null=False, blank=False)

    def __str__(self):
        return str(self.id)


class Media(models.Model):
    id = models.IntegerField(primary_key=True, null=False, blank=False)
    name = models.CharField(max_length=200, null=False, blank=False)
    slug = models.CharField(max_length=200, null=False, blank=False)
    link = models.URLField(
        max_length=200, default='', blank=False, null=False)
    alt = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return str(self.id)


class Post(models.Model):
    id = models.IntegerField(primary_key=True, null=False, blank=False)
    title = models.CharField(
        max_length=200, default='', blank=False, null=False)
    slug = models.CharField(max_length=200, null=False, blank=False)
    body = models.TextField()
    seoTitle = models.CharField(
        max_length=200, default='', blank=False, null=False)
    seoDescription = models.CharField(
        max_length=2000, default='', blank=False, null=False)

    date = models.CharField(max_length=200, null=False, blank=False)

    author = models.CharField(max_length=200, null=True, blank=True)
    categories = models.CharField(max_length=200, null=True, blank=True)
    tags = models.CharField(max_length=200, null=True, blank=True)
    featured_media = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return str(self.id)
