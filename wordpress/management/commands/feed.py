from django.core.management.base import BaseCommand

import requests
import json

from wordpress.models import Author, Category, Media, Post, Tag


class Command(BaseCommand):
    help = 'Get WordPress Contents'

    def add_arguments(self, parser):
        parser.add_argument('functions', nargs='+', type=str)

    def handle(self, *args, **options):
        if "main" in options['functions']:
            self.main()

    def seo(self, id):
        try:
            seoRes = requests.request(
                "GET", "https://www.americanfirearms.org/wp-json/seopress/v1/posts/{}".format(id), headers={}, data={})

            seo = json.loads(seoRes.text)

            return seo['description']

        except Exception as e:
            print(e)
            return ""

    def main(self):

        Author.objects.all().delete()
        Category.objects.all().delete()
        Tag.objects.all().delete()
        Media.objects.all().delete()
        Post.objects.all().delete()

        print('Collecting All posts data...')
        for page in range(1, 50):
            print("Page {}".format(page))

            postsRes = requests.request(
                "GET", "https://www.americanfirearms.org/wp-json/wp/v2/posts?per_page=10&page={}".format(page), headers={}, data={})

            if postsRes.status_code != 200:
                break

            posts = json.loads(postsRes.text)

            for post in posts:
                id = post['id']
                title = post['title']['rendered'].replace('&amp;', '&').strip()
                slug = post['slug']
                body = post['content']['rendered']
                excerpt = self.seo(id)
                date = post['date']
                author = post['author']
                categories = ", ".join(str(c) for c in post['categories'])
                tags = ", ".join(str(t) for t in post['tags'])
                featured_media = post['featured_media']

                try:
                    Post.objects.get(id=id)
                    continue
                except Post.DoesNotExist:
                    pass

                Post.objects.create(
                    id=id,
                    title=title,
                    slug=slug,
                    body=body,
                    excerpt=excerpt,
                    date=date,
                    author=author,
                    categories=categories,
                    tags=tags,
                    featured_media=featured_media
                )

        print('Collecting All authors data...')
        for page in range(1, 5):
            print("Page {}".format(page))

            authorsRes = requests.request(
                "GET", "https://www.americanfirearms.org/wp-json/wp/v2/users?per_page=10&page={}".format(page), headers={}, data={})

            if authorsRes.status_code != 200:
                break

            authors = json.loads(authorsRes.text)

            for author in authors:
                id = author['id']
                name = author['name']
                slug = author['slug']
                description = author['description']

                try:
                    Author.objects.get(id=id)
                    continue
                except Author.DoesNotExist:
                    pass

                Author.objects.create(
                    id=id,
                    name=name,
                    slug=slug,
                    description=description,
                )

        print('Collecting All Categories data...')
        for page in range(1, 5):
            print("Page {}".format(page))

            categoriesRes = requests.request(
                "GET", "https://www.americanfirearms.org/wp-json/wp/v2/categories?per_page=10&page={}".format(page), headers={}, data={})

            if categoriesRes.status_code != 200:
                break

            categories = json.loads(categoriesRes.text)

            for category in categories:
                id = category['id']
                name = category['name']
                slug = category['slug']
                description = category['description']

                try:
                    Category.objects.get(id=id)
                    continue
                except Category.DoesNotExist:
                    pass

                Category.objects.create(
                    id=id,
                    name=name,
                    slug=slug,
                    description=description,
                )

        print('Collecting All Tags data...')
        for page in range(1, 30):
            print("Page {}".format(page))

            tagsRes = requests.request(
                "GET", "https://www.americanfirearms.org/wp-json/wp/v2/tags?per_page=10&page={}".format(page), headers={}, data={})

            if tagsRes.status_code != 200:
                break

            tags = json.loads(tagsRes.text)

            for tag in tags:
                id = tag['id']
                name = tag['name']
                slug = tag['slug']
                description = tag['description']

                try:
                    Tag.objects.get(id=id)
                    continue
                except Tag.DoesNotExist:
                    pass

                Tag.objects.create(
                    id=id,
                    name=name,
                    slug=slug,
                    description=description,
                )

        print('Collecting All Medias data...')
        for page in range(1, 1000):
            print("Page {}".format(page))

            mediasRes = requests.request(
                "GET", "https://www.americanfirearms.org/wp-json/wp/v2/media?per_page=10&page={}".format(page), headers={}, data={})

            if mediasRes.status_code != 200:
                break

            medias = json.loads(mediasRes.text)

            for media in medias:
                id = media['id']
                name = media['title']['rendered']
                slug = media['slug']
                link = media['source_url']
                alt = media['alt_text']

                try:
                    Media.objects.get(id=id)
                    continue
                except Media.DoesNotExist:
                    pass

                Media.objects.create(
                    id=id,
                    name=name,
                    slug=slug,
                    link=link,
                    alt=alt,
                )
