from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget

from posts.models import Author, Category, Image, Post, Tag


class CategoryAdmin(admin.ModelAdmin):
    fields = ['slug', 'name', 'description']
    list_display = ['slug', 'name']
    search_fields = ['slug', 'name', 'description']


class TagAdmin(admin.ModelAdmin):
    fields = ['slug', 'name', 'description']
    list_display = ['slug', 'name']
    search_fields = ['slug', 'name', 'description']


class AuthorAdmin(admin.ModelAdmin):
    fields = ['slug', 'name', 'description', 'avatar']
    list_display = ['slug', 'name', 'avatar']
    search_fields = ['slug', 'name', 'description', 'avatar']


class ImagesInline(admin.TabularInline):
    model = Image
    extra = 0


class PostAdmin(admin.ModelAdmin):
    fields = ['slug', 'old_link', 'title', 'body', 'excerpt',
              'date', 'author', 'categories', 'tags']
    list_display = ['slug', 'title', 'author']
    list_filter = ['categories', 'tags']
    search_fields = ['slug', 'old_link', 'title']

    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

    inlines = [ImagesInline]


class ImageAdmin(admin.ModelAdmin):
    fields = ['slug', 'link', 'alt', 'post', 'type']
    list_filter = ['type']
    list_display = ['slug', 'link', 'alt', 'type']
    search_fields = ['slug', 'link', 'alt', 'type']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Image, ImageAdmin)
