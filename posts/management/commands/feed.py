import json
from django.core.management.base import BaseCommand
import requests

from posts.models import Author, Category, Image, Post, Tag


class Command(BaseCommand):
    help = 'Get WordPress Contents'

    def add_arguments(self, parser):
        parser.add_argument('functions', nargs='+', type=str)

    def handle(self, *args, **options):
        if "posts" in options['functions']:
            self.posts()

    def posts(self):
        Post.objects.all().delete()

        for page in range(1, 40):
            postsRes = requests.request(
                "GET", "https://www.americanfirearms.org/wp-json/wp/v2/posts?per_page=10&page={}".format(page), headers={}, data={})

            posts = json.loads(postsRes.text)

            for post in posts:
                slug = post['slug']
                old_link = post['link']
                title = post['title']['rendered']
                content = post['content']['rendered']
                excerpt = post['excerpt']['rendered']
                date = post['date']

                newPost = Post(
                    slug=slug,
                    old_link=old_link,
                    title=title,
                    content=content,
                    excerpt=excerpt,
                    date=date,
                )

                # Meta
                authorLink = post['_links']['author'][0]['href']
                authorRes = requests.request(
                    "GET", authorLink, headers={}, data={})
                authorData = json.loads(authorRes.text)
                author = Author(
                    slug=authorData['slug'],
                    name=authorData['name'],
                    description=authorData['description'],
                    avatar=authorData['avatar_urls']['96'],
                )
                author.save()
                newPost.author = author
                newPost.save()

                attachmentsLink = post['_links']['wp:attachment'][0]['href']
                attachmentsRes = requests.request(
                    "GET", attachmentsLink, headers={}, data={})
                attachmentsData = json.loads(attachmentsRes.text)
                for attachmentData in attachmentsData:
                    attachment = Image(
                        slug=attachmentData['slug'],
                        link=attachmentData['source_url'],
                        alt=attachmentData['alt_text'],
                        type='attachment',
                        post=newPost
                    )
                    attachment.save()

                featuredMediaLink = post['_links']['wp:featuredmedia'][0]['href']
                featuredMediaRes = requests.request(
                    "GET", featuredMediaLink, headers={}, data={})
                featuredMediaData = json.loads(featuredMediaRes.text)
                featuredMedia = Image(
                    slug=featuredMediaData['slug'],
                    link=featuredMediaData['source_url'],
                    alt=featuredMediaData['alt_text'],
                    type='thumbnail',
                    post=newPost
                )
                featuredMedia.save()

                categoriesLink = post['_links']['wp:term'][0]['href']
                categoriesRes = requests.request(
                    "GET", categoriesLink, headers={}, data={})
                categoriesData = json.loads(categoriesRes.text)
                for categoryData in categoriesData:
                    category = Category(
                        slug=categoryData['slug'],
                        name=categoryData['name'],
                        description=categoryData['description'],
                    )
                    category.save()
                    newPost.categories.add(category)

                tagsLink = post['_links']['wp:term'][1]['href']
                tagsRes = requests.request(
                    "GET", tagsLink, headers={}, data={})
                tagsData = json.loads(tagsRes.text)
                for tagData in tagsData:
                    tag = Tag(
                        slug=tagData['slug'],
                        name=tagData['name'],
                        description=tagData['description'],
                    )
                    tag.save()
                    newPost.tags.add(tag)

                print("Post {} has been saved successfully".format(newPost.slug))
