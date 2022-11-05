from django.contrib import admin

from .models import Author, Category, Post, Tag, Media


class AuthorAdmin(admin.ModelAdmin):
    fields = ['id', 'name', 'slug', 'description']
    list_display = ['id', 'name']
    search_fields = ['id', 'name']


class CategoryAdmin(admin.ModelAdmin):
    fields = ['id', 'name', 'slug', 'description']
    list_display = ['id', 'name']
    search_fields = ['id', 'name']


class TagAdmin(admin.ModelAdmin):
    fields = ['id', 'name', 'slug', 'description']
    list_display = ['id', 'name']
    search_fields = ['id', 'name']


class MediaAdmin(admin.ModelAdmin):
    fields = ['id', 'name', 'slug', 'link', 'alt']
    list_display = ['id', 'name']
    search_fields = ['id', 'name']


class PostAdmin(admin.ModelAdmin):
    fields = ['id', 'title', 'slug', 'body', 
              'date', 'author', 'categories', 'tags', 'featured_media']
    list_display = ['id', 'title']
    search_fields = ['id', 'title']


admin.site.register(Author, AuthorAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Media, MediaAdmin)
admin.site.register(Post, PostAdmin)
