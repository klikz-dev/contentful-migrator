from django.core.management.base import BaseCommand

import json
from tempfile import NamedTemporaryFile
from bs4 import BeautifulSoup
import html
import requests
import base64

from wordpress.models import Author, Category, Media, Post, Tag


class Command(BaseCommand):
    help = 'Get WordPress Contents'

    def add_arguments(self, parser):
        parser.add_argument('functions', nargs='+', type=str)

    def handle(self, *args, **options):
        if "main" in options['functions']:
            self.main()

    def convertHTMLToACFJson(self, content):
        soup = BeautifulSoup(content, 'html.parser')

        elements = soup.find_all(
            ['h2', 'h3', 'h4', 'p', 'span', 'a', 'div', 'ol', 'ul', 'table'])

        contents = []
        for element in elements:
            if element.name == 'h2':
                if element.get_text() == "":
                    continue

                content = {
                    "acf_fc_layout": "heading",
                    "text": element.get_text().strip()
                }

                contents.append(content)

            if element.name == 'h3':
                if element.get_text() == "":
                    continue

                if element.has_attr('class') and 'elementor-cta__title' in element['class']:
                    continue

                if "The Latest" in element.get_text() and "Reviews:" in element.get_text():
                    continue

                if "More on" in element.get_text() and ":" in element.get_text():
                    continue

                content = {
                    "acf_fc_layout": "text",
                    "body": "<h3>{}</h3>".format(element.get_text().strip())
                }

                contents.append(content)

            if element.name == 'h4':
                if element.get_text() == "":
                    continue

                if element.has_attr('class') and 'elementor-toc__header-title' in element['class']:
                    continue

                if element.has_attr('class') and 'elementor-cta__title' in element['class']:
                    continue

                if 'Performance Scorecard' in element.get_text():
                    continue

                parent = element.parent
                if parent.has_attr('class') and 'elementor-post__text' in parent['class']:
                    continue

                content = {
                    "acf_fc_layout": "text",
                    "body": "<h4>{}</h4>".format(element.get_text().strip())
                }

                contents.append(content)

            if element.name == 'p':
                if element.get_text() == "":
                    continue

                parent = element.parent
                if parent.has_attr('class') and 'elementor-post__excerpt' in parent['class']:
                    continue

                if parent.has_attr('class') and 'elementor-tab-content' in parent['class']:
                    continue

                span = element.find('span')
                if span and span.get_text() == element.get_text():
                    continue

                childContents = ""
                for child in element.children:
                    try:
                        if child.name == 'a':
                            link = child.get('href').replace(
                                'https://www.americanfirearms.org', '')

                            childContent = "<a href='{}'>{}</a>".format(
                                link, child.get_text())

                        elif child.name != None and len(child.find_all('a')) > 0:
                            link = child.find_all('a')[0].get('href').replace(
                                'https://www.americanfirearms.org', '')

                            childContent = "<a href='{}'>{}</a>".format(
                                link, child.find_all('a')[0].get_text())

                        else:
                            childContent = child.get_text()

                        childContents += childContent
                    except:
                        continue

                content = {
                    "acf_fc_layout": "text",
                    "body": "<p>{}</p>".format(childContents)
                }

                contents.append(content)

            if element.name == 'span':
                if element.get_text() == "":
                    continue

                parent = element.parent
                if parent.name != 'p' or parent.get_text() != element.get_text():
                    continue

                childContents = ""
                for child in element.children:
                    try:
                        if child.name == 'a':
                            link = child.get('href').replace(
                                'https://www.americanfirearms.org', '')

                            childContent = "<a href='{}'>{}</a>".format(
                                link, child.get_text())

                        if child.name != None and len(child.find_all('a')) > 0:
                            link = child.find_all('a')[0].get('href').replace(
                                'https://www.americanfirearms.org', '')

                            childContent = "<a href='{}'>{}</a>".format(
                                link, child.find_all('a')[0].get_text())

                        else:
                            childContent = child.get_text()

                        childContents += childContent
                    except:
                        continue

                content = {
                    "acf_fc_layout": "text",
                    "body": "<p>{}</p>".format(childContents)
                }

                contents.append(content)

            if element.name == 'a' and element.has_attr('class') and 'elementor-cta' in element['class']:
                try:
                    ctaTitle = element.select(
                        '.elementor-cta__title')[0].get_text().strip()

                    ctaLink = element.get('href').replace(
                        'https://www.americanfirearms.org', '')

                    ctaImage = element.select('.elementor-cta__bg')[0]['style'].replace(
                        'background-image: url(', '').replace(');', '')
                    ctaImageId = self.wpMedia(ctaImage, ctaTitle)

                    if ctaImageId == "":
                        continue

                    ctaButtonText = element.select(
                        '.elementor-cta__button')[0].get_text().strip()

                    try:
                        ctaPrice = int(element.select(
                            '.elementor-ribbon-inner')[0].get_text().strip().replace('$', '').replace(',', '').replace('\u200e', ''))
                    except:
                        ctaPrice = 0
                except Exception as e:
                    print(e)
                    continue

                content = {
                    "acf_fc_layout": "cta",
                    "title": ctaTitle,
                    "link": ctaLink,
                    "image": ctaImageId,
                    "button_text": ctaButtonText,
                    "price": ctaPrice,
                }

                contents.append(content)

            if element.name == 'div' and element.has_attr('class'):
                if 'elementor-widget-accordion' in element['class']:
                    items = element.select('.elementor-accordion-item')
                    if len(items) == 0:
                        continue

                    accordionsData = []

                    for item in items:
                        itemHead = item.select(
                            '.elementor-tab-title')[0].get_text().strip().replace('"', '“')
                        itemContent = item.select(
                            '.elementor-tab-content')[0].get_text().strip().replace('"', '“')

                        accordionsData.append(
                            {"question": itemHead, "answer": itemContent})

                    content = {
                        "acf_fc_layout": "faq",
                        "q_&_a": accordionsData
                    }

                    contents.append(content)

                if 'elementor-widget-image' in element['class']:
                    try:
                        image = element.select('img')[0]['data-src']

                        alt = ""
                        if len(element.select('figcaption')) > 0:
                            alt = element.select('figcaption')[
                                0].get_text().strip()
                        else:
                            alt = element.select('img')[0]['alt'].strip()

                        imageId = self.wpMedia(image, alt)
                        if imageId == "":
                            continue
                    except Exception as e:
                        print(e)
                        continue

                    content = {
                        "acf_fc_layout": "image",
                        "image": imageId,
                        "description": alt

                    }

                    contents.append(content)

                elif 'elementor-row' in element['class']:
                    try:
                        ratings = element.select(
                            '.elementor-star-rating__wrapper')
                        if len(ratings) == 0:
                            continue

                        tableData = []

                        for rating in ratings:
                            performance = rating.select(
                                '.elementor-star-rating__title')[0].get_text().replace(':', '').strip()

                            score = rating.select(
                                '.elementor-star-rating')[0]['title']

                            tableData.append([performance, score])
                    except Exception as e:
                        print(e)
                        continue

                    content = {
                        "acf_fc_layout": "performance_scoreboard",
                        "board": tableData
                    }

                    contents.append(content)

                elif 'elementor-widget-video' in element['class']:
                    try:
                        video = json.loads(element['data-settings'])

                        content = {
                            "acf_fc_layout": "youtube",
                            "url": video['youtube_url']
                        }
                    except Exception as e:
                        print(e)
                        continue

                    contents.append(content)

                elif 'aawp-product' in element['class']:
                    try:
                        productId = element['data-aawp-product-id']
                    except Exception as e:
                        print(e)
                        continue

                    content = {
                        "acf_fc_layout": "amazon_product",
                        "product_id": productId
                    }

                    contents.append(content)

                else:
                    continue

            if element.name == 'ul':
                if element.parent.has_attr('class') and 'aawp-product__description' in element.parent['class']:
                    continue

                ulContents = ""
                for child in element.children:
                    if child == "":
                        continue

                    liContents = ""

                    if child.name == None:
                        liContents = child
                    else:
                        for grandchild in child.children:
                            try:
                                if grandchild.name == 'a':
                                    link = grandchild.get('href').replace(
                                        'https://www.americanfirearms.org', '')

                                    liContent = "<a href='{}'>{}</a>".format(
                                        link, grandchild.get_text())

                                elif grandchild.name != None and len(grandchild.find_all('a')) > 0:
                                    link = grandchild.find_all('a')[0].get('href').replace(
                                        'https://www.americanfirearms.org', '')

                                    liContent = "<a href='{}'>{}</a>".format(
                                        link, grandchild.find_all('a')[0].get_text())

                                elif grandchild.name == 'strong':
                                    liContent = "<strong>{}</strong>".format(
                                        grandchild.get_text())

                                else:
                                    liContent = grandchild.get_text()
                            except:
                                continue

                            liContents += liContent

                    if "{}".format(liContents) == "":
                        continue

                    ulContents += "<li>{}</li>".format(liContents)

                content = {
                    "acf_fc_layout": "text",
                    "body": "<ul>{}</ul>".format(ulContents)
                }

                contents.append(content)

            if element.name == 'ol':
                if element.parent.has_attr('class') and 'aawp-product__description' in element.parent['class']:
                    continue

                olContents = ""
                for child in element.children:
                    if child == "":
                        continue

                    liContents = ""

                    if child.name == None:
                        liContents = child
                    else:
                        for grandchild in child.children:
                            try:
                                if grandchild.name == 'a':
                                    link = grandchild.get('href').replace(
                                        'https://www.americanfirearms.org', '')

                                    liContent = "<a href='{}'>{}</a>".format(
                                        link, grandchild.get_text())

                                elif grandchild.name != None and len(grandchild.find_all('a')) > 0:
                                    link = grandchild.find_all('a')[0].get('href').replace(
                                        'https://www.americanfirearms.org', '')

                                    liContent = "<a href='{}'>{}</a>".format(
                                        link, grandchild.find_all('a')[0].get_text())

                                elif grandchild.name == 'strong':
                                    liContent = "<strong>{}</strong>".format(
                                        grandchild.get_text())

                                else:
                                    liContent = grandchild.get_text()

                                liContents += liContent
                            except:
                                continue

                    if "{}".format(liContents) == "":
                        continue

                    olContents += "<li>{}</li>".format(liContents)

                content = {
                    "acf_fc_layout": "text",
                    "body": "<ol>{}</ol>".format(olContents)
                }

                contents.append(content)

            if element.name == 'table':
                tableData = []

                useHeader = False
                trs = element.find_all('tr')
                for tr in trs:
                    row = ""
                    tds = tr.find_all(['th', 'td'])
                    for td in tds:
                        if td.name == 'th':
                            useHeader = True

                        if len(td.find_all('a')) > 0:
                            link = td.find_all('a')[0].get('href').replace(
                                'https://www.americanfirearms.org', '')
                            name = td.find_all('a')[0].get_text()

                            data = "<a href='{}'>{}</a>".format(link, name)

                        elif len(td.find_all('img')) > 0:
                            if td.find_previous_sibling('td') != None:
                                data = td.get_text()

                            else:
                                image = td.select('img')[0]['data-src']
                                alt = td.select('img')[0]['alt'].strip()
                                if alt == "":
                                    alt = td.find_next_sibling('td').get_text()

                                data = "<img src='{}' alt='{}' />".format(
                                    image, alt)
                                continue

                        else:
                            data = td.get_text()
                            if data == "Image":
                                continue

                        if row == "":
                            row = "{}".format(data)
                        else:
                            row += ", {}".format(data)

                    tableData.append({
                        "columns": row
                    })

                content = {
                    "acf_fc_layout": "table",
                    "table_header": useHeader,
                    "row": tableData
                }

                contents.append(content)

        description = ""
        isDesc = True
        mergedContents = []
        for content in contents:
            if isDesc and content['acf_fc_layout'] != "text":
                isDesc = False

            if isDesc:
                description += content['body']
            else:
                if len(mergedContents) != 0 and mergedContents[-1]['acf_fc_layout'] == "text" and content['acf_fc_layout'] == "text":
                    mergedContents[-1]['body'] = mergedContents[-1]['body'] + \
                        content['body']
                else:
                    mergedContents.append(content)

        return {
            "description": description,
            "acf": {
                "contents": mergedContents
            }
        }

    def main(self):
        # Getting Existing Post slugs
        slugs = []
        for i in range(1, 10):
            wpPosts = requests.request(
                "GET",
                "https://firearms-wp.klikz.us/wp-json/wp/v2/posts?page={}&per_page=100".format(
                    i)
            )
            if wpPosts.status_code != 200:
                break

            for wpPost in json.loads(wpPosts.text):
                print(wpPost['slug'])
                slugs.append(wpPost['slug'])

        # Process All Posts
        posts = Post.objects.all()

        # Process a specifi post
        # posts = Post.objects.filter(slug="gun-brands")

        for post in posts:
            print("--------------------------------------------------------")

            if 'et_pb_section' in post.body or 'bb_built' in post.body or 'et_pb_row' in post.body:
                print("Post {} contains buggy html".format(post.title))
                continue
            #################################

            # Skip existing posts
            if post.slug in slugs:
                print("Ignoring Post {}".format(post.slug))
                continue
            #################################

            print("Processing Post {}".format(post.slug))

            title = html.unescape(post.title)
            content = html.unescape(post.seoDescription)
            slug = post.slug
            date = post.date

            body = self.convertHTMLToACFJson(post.body)
            acf = body['acf']
            if body['description'] != "":
                content = body['description']

            # Categories
            categories = []
            for categoryId in post.categories.split(','):
                if categoryId != "":
                    category = Category.objects.get(id=categoryId)

                    wpCategory = self.wpCategory(
                        category.slug,
                        html.unescape(category.name),
                        html.unescape(category.description)
                    )
                    if wpCategory != 0:
                        categories.append(int(wpCategory))

            # Tags
            tags = []
            for tagId in post.tags.split(','):
                if tagId != "":
                    tag = Tag.objects.get(id=tagId)

                    wpTag = self.wpTag(
                        tag.slug,
                        html.unescape(tag.name),
                        html.unescape(tag.description)
                    )
                    if wpTag != 0:
                        tags.append(int(wpTag))

            # Thumbnail
            try:
                featured_media = Media.objects.get(id=post.featured_media)

                mediaLink = featured_media.link
                mediaAlt = featured_media.alt
                if mediaAlt == "":
                    mediaAlt = title

                featuredMediaId = self.wpMedia(mediaLink, mediaAlt)
            except Media.DoesNotExist:
                featuredMediaId = 0

            # Create Post
            postId = self.wpPost({
                "slug": slug,
                "title": title,
                "status": "publish",
                "acf": acf,
                "date": date,
                "categories": categories,
                "tags": tags,
                "featured_media": featuredMediaId,
                "content": content
            })

            print("Successfully Created a Post {}".format(postId))

    def wpAuth(self):
        credentials = 'admin:CqDQ 7EPD vizZ s14b 5pEx vP6i'
        token = base64.b64encode(credentials.encode())
        headers = {
            'Authorization': 'Basic ' + token.decode('utf-8'),
            'Content-Type': 'application/json'
        }

        return headers

    def wpFileAuth(self):
        credentials = 'admin:CqDQ 7EPD vizZ s14b 5pEx vP6i'
        token = base64.b64encode(credentials.encode())
        headers = {
            'Authorization': 'Basic ' + token.decode('utf-8')
        }

        return headers

    def wpCategory(self, slug, name, description):
        print("Creating Category {}".format(slug))

        try:
            categories = requests.get(
                "https://firearms-wp.klikz.us/wp-json/wp/v2/categories?slug={}".format(slug))

            if len(json.loads(categories.text)) > 0:
                id = json.loads(categories.text)[0]['id']

                print("Category: {} already exists. Id: {}".format(name, id))
                return id

            response = requests.post(
                "https://firearms-wp.klikz.us/wp-json/wp/v2/categories", headers=self.wpAuth(),
                data=json.dumps({
                    "slug": slug,
                    "name": name,
                    "description": description
                })
            )
            categoryId = json.loads(response.text)['id']
            print("Created Category {}".format(categoryId))
            return categoryId

        except Exception as e:
            print(e)
            print(response.text)
            print("Failed creating category")
            return 0

    def wpTag(self, slug, name, description):
        print("Creating Tag {}".format(slug))

        try:
            tags = requests.get(
                "https://firearms-wp.klikz.us/wp-json/wp/v2/tags?slug={}".format(slug))

            if len(json.loads(tags.text)) > 0:
                tagId = json.loads(tags.text)[0]['id']

                print("Tag: {} already exists. Id: {}".format(name, tagId))
                return tagId

            response = requests.post(
                "https://firearms-wp.klikz.us/wp-json/wp/v2/tags", headers=self.wpAuth(),
                data=json.dumps({
                    "slug": slug,
                    "name": name,
                    "description": description
                })
            )
            tagId = json.loads(response.text)['id']
            print("Created Tag {}".format(tagId))
            return tagId

        except Exception as e:
            print(e)
            print(response.text)
            print("Failed creating tag")
            return 0

    def wpMedia(self, mediaLink, mediaAlt):
        print("Uploading image {}".format(mediaLink))

        raw = requests.get(mediaLink).content
        with NamedTemporaryFile(delete=False, mode="wb", suffix=".jpg") as img:
            img.write(raw)

            file = open(img.name, "rb")
            media = {'file': file, 'caption': mediaAlt}

            try:
                response = requests.post(
                    "https://firearms-wp.klikz.us/wp-json/wp/v2/media", headers=self.wpFileAuth(),
                    files=media
                )
                imageId = json.loads(response.text)['id']
                print("Uploaded image {}".format(imageId))
                return imageId
            except Exception as e:
                print(e)
                print(response.text)
                print("Failed image upload")
                return 0

    def wpPost(self, data):
        print("Creating Post {}".format(data['slug']))

        posts = requests.request(
            "GET",
            "https://firearms-wp.klikz.us/wp-json/wp/v2/posts?slug={}".format(
                data['slug'])
        )

        if len(json.loads(posts.text)) > 0:
            try:
                postId = json.loads(posts.text)[0]['id']
                print("Post: {} already exists. Id: {}".format(
                    data['title'], postId))

                response = requests.request(
                    "PUT",
                    "https://firearms-wp.klikz.us/wp-json/wp/v2/posts/{}".format(postId), headers=self.wpAuth(),
                    data=json.dumps(data)
                )
                postId = json.loads(response.text)['id']
                print("Updated Post {}".format(postId))
                return postId
            except Exception as e:
                print(e)
                print(response.text)
                print("Failed updating post")
                return 0
        else:
            try:
                response = requests.request(
                    "POST",
                    "https://firearms-wp.klikz.us/wp-json/wp/v2/posts", headers=self.wpAuth(),
                    data=json.dumps(data)
                )
                postId = json.loads(response.text)['id']
                print("Created Post {}".format(postId))
                return postId
            except Exception as e:
                print(e)
                print(response.text)
                print("Failed creating post")
                return 0
