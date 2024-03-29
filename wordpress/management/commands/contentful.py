from django.core.management.base import BaseCommand

import json
from bs4 import BeautifulSoup
import html

from library.contentful import contentfulFAQ, contentfulImage, contentfulCTA, contentfulPost, contentfulTable, contentfulScorecard, contentfulEmbed, contentfulAffiliate, contentfulAuthor, contentfulCategory, contentfulTag
from wordpress.models import Author, Category, Media, Post, Tag


class Command(BaseCommand):
    help = 'Get WordPress Contents'

    def add_arguments(self, parser):
        parser.add_argument('functions', nargs='+', type=str)

    def handle(self, *args, **options):
        if "main" in options['functions']:
            self.main()

    def convertHTMLToContentfulJson(self, content):
        soup = BeautifulSoup(content, 'html.parser')

        elements = soup.find_all(
            ['h1', 'h2', 'h3', 'h4', 'p', 'span', 'a', 'div', 'ol', 'ul', 'table'])

        # Tmp values
        firstH2 = ""
        latestH3 = ""

        contents = []
        for element in elements:
            if element.name == 'h1':
                if element.get_text() == "":
                    continue

                content = {
                    "data": {},
                    "content": [
                        {
                            "data": {},
                            "marks": [],
                            "value": element.get_text().strip(),
                            "nodeType": "text"
                        }
                    ],
                    "nodeType": "heading-1"
                }

                contents.append(content)

            if element.name == 'h2':
                if element.get_text() == "":
                    continue

                content = {
                    "data": {},
                    "content": [
                        {
                            "data": {},
                            "marks": [],
                            "value": element.get_text().strip(),
                            "nodeType": "text"
                        }
                    ],
                    "nodeType": "heading-2"
                }

                if firstH2 == "":
                    firstH2 = element.get_text().strip()

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
                    "data": {},
                    "content": [
                        {
                            "data": {},
                            "marks": [],
                            "value": element.get_text().strip(),
                            "nodeType": "text"
                        }
                    ],
                    "nodeType": "heading-3"
                }

                contents.append(content)

                latestH3 = element.get_text().strip()

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
                    "data": {},
                    "content": [
                        {
                            "data": {},
                            "marks": [],
                            "value": element.get_text().strip(),
                            "nodeType": "text"
                        }
                    ],
                    "nodeType": "heading-4"
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

                childContents = []
                for child in element.children:
                    if child.name == 'a':
                        link = child.get('href').replace(
                            'https://www.americanfirearms.org', '')

                        childContent = {
                            "nodeType": "hyperlink",
                            "content": [
                                {
                                    "nodeType": "text",
                                    "value": child.get_text(),
                                    "marks": [],
                                    "data": {}
                                }
                            ],
                            "data": {
                                "uri": link
                            }
                        }

                    elif child.name != None and len(child.find_all('a')) > 0:
                        link = child.find_all('a')[0].get('href').replace(
                            'https://www.americanfirearms.org', '')

                        childContent = {
                            "nodeType": "hyperlink",
                            "content": [
                                {
                                    "nodeType": "text",
                                    "value": child.find_all('a')[0].get_text(),
                                    "marks": [],
                                    "data": {}
                                }
                            ],
                            "data": {
                                "uri": link
                            }
                        }

                    else:
                        childContent = {
                            "data": {},
                            "marks": [],
                            "value": child.get_text(),
                            "nodeType": "text"
                        }

                    childContents.append(childContent)

                content = {
                    "data": {},
                    "content": childContents,
                    "nodeType": "paragraph"
                }

                contents.append(content)

            if element.name == 'span':
                if element.get_text() == "":
                    continue

                parent = element.parent
                if parent.name != 'p' or parent.get_text() != element.get_text():
                    continue

                childContents = []
                for child in element.children:
                    if child.name == 'a':
                        link = child.get('href').replace(
                            'https://www.americanfirearms.org', '')

                        childContent = {
                            "nodeType": "hyperlink",
                            "content": [
                                {
                                    "nodeType": "text",
                                    "value": child.get_text(),
                                    "marks": [],
                                    "data": {}
                                }
                            ],
                            "data": {
                                "uri": link
                            }
                        }

                    if child.name != None and len(child.find_all('a')) > 0:
                        link = child.find_all('a')[0].get('href').replace(
                            'https://www.americanfirearms.org', '')

                        childContent = {
                            "nodeType": "hyperlink",
                            "content": [
                                {
                                    "nodeType": "text",
                                    "value": child.find_all('a')[0].get_text(),
                                    "marks": [],
                                    "data": {}
                                }
                            ],
                            "data": {
                                "uri": link
                            }
                        }

                    else:
                        childContent = {
                            "data": {},
                            "marks": [],
                            "value": child.get_text(),
                            "nodeType": "text"
                        }

                    childContents.append(childContent)

                content = {
                    "data": {},
                    "content": childContents,
                    "nodeType": "paragraph"
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
                    ctaImageId = contentfulImage(ctaImage, ctaTitle)

                    if ctaImageId == "":
                        continue

                    ctaButtonText = element.select(
                        '.elementor-cta__button')[0].get_text().strip()

                    ctaPrice = element.select(
                        '.elementor-ribbon-inner')[0].get_text().strip().replace('$', '').replace(',', '').replace('\u200e', '')

                    cta = contentfulCTA(
                        ctaTitle, ctaLink, ctaImageId, ctaButtonText, ctaPrice)
                except Exception as e:
                    print(e)
                    continue

                content = {
                    "nodeType": "embedded-entry-block",
                    "content": [],
                    "data": {
                        "target": {
                            "sys": {
                                "id": cta,
                                "type": "Link",
                                "linkType": "Entry"
                            }
                        }
                    }
                }

                contents.append(content)

            if element.name == 'div' and element.has_attr('class'):
                if 'elementor-widget-accordion' in element['class']:
                    items = element.select('.elementor-accordion-item')
                    if len(items) == 0:
                        continue

                    accordionsData = []
                    accordionsData.append(['Question', 'Answer'])

                    for item in items:
                        itemHead = item.select(
                            '.elementor-tab-title')[0].get_text().strip().replace('"', '“')
                        itemContent = item.select(
                            '.elementor-tab-content')[0].get_text().strip().replace('"', '“')

                        accordionsData.append([itemHead, itemContent])

                    accordion = contentfulFAQ(firstH2, accordionsData)

                    content = {
                        "nodeType": "embedded-entry-block",
                        "content": [],
                        "data": {
                            "target": {
                                "sys": {
                                    "id": accordion,
                                    "type": "Link",
                                    "linkType": "Entry"
                                }
                            }
                        }
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

                        imageId = contentfulImage(image, alt)
                        if imageId == "":
                            continue

                    except Exception as e:
                        print(e)
                        continue

                    content = {
                        "nodeType": "embedded-asset-block",
                        "content": [],
                        "data": {
                            "target": {
                                "sys": {
                                    "id": imageId,
                                    "type": "Link",
                                    "linkType": "Asset"
                                }
                            }
                        }
                    }

                    contents.append(content)

                elif 'elementor-row' in element['class']:
                    try:
                        ratings = element.select(
                            '.elementor-star-rating__wrapper')
                        if len(ratings) == 0:
                            continue

                        tableData = []
                        tableData.append(['Performance', 'Score'])

                        for rating in ratings:
                            performance = rating.select(
                                '.elementor-star-rating__title')[0].get_text().replace(':', '').strip()

                            score = rating.select(
                                '.elementor-star-rating')[0]['title']

                            tableData.append([performance, score])

                        cardName = latestH3[3:].strip()
                        scorecard = contentfulScorecard(cardName, tableData)

                    except Exception as e:
                        print(e)
                        continue

                    content = {
                        "nodeType": "embedded-entry-block",
                        "content": [],
                        "data": {
                            "target": {
                                "sys": {
                                    "id": scorecard,
                                    "type": "Link",
                                    "linkType": "Entry"
                                }
                            }
                        }
                    }

                    contents.append(content)

                elif 'elementor-widget-video' in element['class']:
                    try:
                        video = json.loads(element['data-settings'])
                        embed = contentfulEmbed(video['youtube_url'])

                        content = {
                            "nodeType": "embedded-entry-block",
                            "content": [],
                            "data": {
                                "target": {
                                    "sys": {
                                        "id": embed,
                                        "type": "Link",
                                        "linkType": "Entry"
                                    }
                                }
                            }
                        }

                    except Exception as e:
                        print(e)
                        continue

                    contents.append(content)

                elif 'aawp-product' in element['class']:
                    try:
                        productId = element['data-aawp-product-id']
                        affiliate = contentfulAffiliate(productId)

                    except Exception as e:
                        print(e)
                        continue

                    content = {
                        "nodeType": "embedded-entry-block",
                        "content": [],
                        "data": {
                            "target": {
                                "sys": {
                                    "id": affiliate,
                                    "type": "Link",
                                    "linkType": "Entry"
                                }
                            }
                        }
                    }

                    contents.append(content)

                else:
                    continue

            if element.name == 'ul':
                if element.parent.has_attr('class') and 'aawp-product__description' in element.parent['class']:
                    continue

                ulContents = []
                for child in element.children:
                    liContents = []
                    try:
                        for grandchild in child.children:
                            if grandchild.name == 'a':
                                link = grandchild.get('href').replace(
                                    'https://www.americanfirearms.org', '')

                                liContent = {
                                    "nodeType": "hyperlink",
                                    "content": [
                                        {
                                            "nodeType": "text",
                                            "value": grandchild.get_text(),
                                            "marks": [],
                                            "data": {}
                                        }
                                    ],
                                    "data": {
                                        "uri": link
                                    }
                                }

                            elif grandchild.name != None and len(grandchild.find_all('a')) > 0:
                                link = grandchild.find_all('a')[0].get('href').replace(
                                    'https://www.americanfirearms.org', '')

                                liContent = {
                                    "nodeType": "hyperlink",
                                    "content": [
                                        {
                                            "nodeType": "text",
                                            "value": grandchild.find_all('a')[0].get_text(),
                                            "marks": [],
                                            "data": {}
                                        }
                                    ],
                                    "data": {
                                        "uri": link
                                    }
                                }

                            elif grandchild.name == 'strong':
                                liContent = {
                                    "data": {},
                                    "marks": [
                                        {
                                            "type": "bold"
                                        }
                                    ],
                                    "value": grandchild.get_text(),
                                    "nodeType": "text"
                                }

                            else:
                                liContent = {
                                    "data": {},
                                    "marks": [],
                                    "value": grandchild.get_text(),
                                    "nodeType": "text"
                                }

                            liContents.append(liContent)
                    except Exception as e:
                        print(e)
                        continue

                    ulContent = {
                        "nodeType": "list-item",
                        "content": [
                            {
                                "nodeType": "paragraph",
                                "content": liContents,
                                "data": {}
                            }
                        ],
                        "data": {}
                    }

                    ulContents.append(ulContent)

                content = {
                    "nodeType": "unordered-list",
                    "content": ulContents,
                    "data": {}
                }

                contents.append(content)

            if element.name == 'ol':
                if element.parent.has_attr('class') and 'aawp-product__description' in element.parent['class']:
                    continue

                olContents = []
                for child in element.children:
                    liContents = []
                    try:
                        for grandchild in child.children:
                            if grandchild.name == 'a':
                                link = grandchild.get('href').replace(
                                    'https://www.americanfirearms.org', '')

                                liContent = {
                                    "nodeType": "hyperlink",
                                    "content": [
                                        {
                                            "nodeType": "text",
                                            "value": grandchild.get_text(),
                                            "marks": [],
                                            "data": {}
                                        }
                                    ],
                                    "data": {
                                        "uri": link
                                    }
                                }

                            elif grandchild.name != None and len(grandchild.find_all('a')) > 0:
                                link = grandchild.find_all('a')[0].get('href').replace(
                                    'https://www.americanfirearms.org', '')

                                liContent = {
                                    "nodeType": "hyperlink",
                                    "content": [
                                        {
                                            "nodeType": "text",
                                            "value": grandchild.find_all('a')[0].get_text(),
                                            "marks": [],
                                            "data": {}
                                        }
                                    ],
                                    "data": {
                                        "uri": link
                                    }
                                }

                            elif grandchild.name == 'strong':
                                liContent = {
                                    "data": {},
                                    "marks": [
                                        {
                                            "type": "bold"
                                        }
                                    ],
                                    "value": grandchild.get_text(),
                                    "nodeType": "text"
                                }

                            else:
                                liContent = {
                                    "data": {},
                                    "marks": [],
                                    "value": grandchild.get_text(),
                                    "nodeType": "text"
                                }

                            liContents.append(liContent)
                    except Exception as e:
                        print(e)
                        continue

                    olContent = {
                        "nodeType": "list-item",
                        "content": [
                            {
                                "nodeType": "paragraph",
                                "content": liContents,
                                "data": {}
                            }
                        ],
                        "data": {}
                    }

                    olContents.append(olContent)

                content = {
                    "nodeType": "ordered-list",
                    "content": olContents,
                    "data": {}
                }

                contents.append(content)

            if element.name == 'table':
                tableData = []
                thumbnails = []

                trs = element.find_all('tr')
                for tr in trs:
                    row = []
                    tds = tr.find_all(['th', 'td'])
                    for td in tds:
                        if len(td.find_all('a')) > 0:
                            link = td.find_all('a')[0].get('href').replace(
                                'https://www.americanfirearms.org', '')
                            name = td.find_all('a')[0].get_text()

                            data = "{} || {}".format(name, link)

                        elif len(td.find_all('img')) > 0:
                            if td.find_previous_sibling('td') != None:
                                data = td.get_text()

                            else:

                                image = td.select('img')[0]['data-src']
                                alt = td.select('img')[0]['alt'].strip()
                                if alt == "":
                                    alt = td.find_next_sibling('td').get_text()

                                imageId = contentfulImage(image, alt)
                                if imageId == "":
                                    continue

                                thumbnail = {
                                    "sys": {
                                        "type": "Link",
                                        "linkType": "Asset",
                                        "id": imageId
                                    }
                                }

                                thumbnails.append(thumbnail)
                                continue

                        else:
                            data = td.get_text()
                            if data == "Image":
                                continue

                        row.append(data)

                    tableData.append(row)

                tableName = soup.find('h2').get_text()
                table = contentfulTable(tableName, tableData, thumbnails)

                content = {
                    "nodeType": "embedded-entry-block",
                    "content": [],
                    "data": {
                        "target": {
                            "sys": {
                                "id": table,
                                "type": "Link",
                                "linkType": "Entry"
                            }
                        }
                    }
                }

                contents.append(content)

        return {
            "data": {},
            "content": contents,
            "nodeType": "document"
        }

    def cleanExcerpt(self, excerpt):
        soup = BeautifulSoup(excerpt, 'html.parser')

        return soup.get_text()

    def cleanDescription(self, excerpt):
        soup = BeautifulSoup(excerpt, 'html.parser')

        contents = []
        for element in soup.children:
            if element.get_text().strip() == "":
                continue

            if element.name == 'a':
                link = element.get('href').replace(
                    'https://www.americanfirearms.org', '')

                content = {
                    "nodeType": "hyperlink",
                    "content": [
                        {
                            "nodeType": "text",
                            "value": element.get_text(),
                            "marks": [],
                            "data": {}
                        }
                    ],
                    "data": {
                        "uri": link
                    }
                }

            elif element.name != None and len(element.find_all('a')) > 0:
                link = element.find_all('a')[0].get('href').replace(
                    'https://www.americanfirearms.org', '')

                content = {
                    "nodeType": "hyperlink",
                    "content": [
                        {
                            "nodeType": "text",
                            "value": element.find_all('a')[0].get_text(),
                            "marks": [],
                            "data": {}
                        }
                    ],
                    "data": {
                        "uri": link
                    }
                }

            else:
                content = {
                    "data": {},
                    "marks": [],
                    "value": element.get_text(),
                    "nodeType": "text"
                }

            contents.append(content)

        return {
            "data": {},
            "content": [{
                "data": {},
                "content": contents,
                "nodeType": "paragraph"
            }],
            "nodeType": "document"
        }

    def main(self):

        print('Uploading posts to Contentful...')

        posts = Post.objects.all()
        # posts = Post.objects.filter(
        #     slug='what-happened-when-washington-dc-banned-guns')

        for post in posts:
            try:
                print("--------------------------------------------------------")

                if 'et_pb_section' in post.body or 'bb_built' in post.body or 'et_pb_row' in post.body:
                    print("Post {} contains buggy html".format(post.title))
                    continue
                #################################

                print("Processing Post {}".format(post.title))

                # Main
                title = html.unescape(post.title)
                slug = post.slug
                seoTitle = html.unescape(post.seoTitle)
                seoDescription = html.unescape(post.seoDescription)
                body = self.convertHTMLToContentfulJson(post.body)
                date = post.date

                thumbnail = {}
                author = {}

                # Thumbnail
                try:
                    featured_media = Media.objects.get(id=post.featured_media)

                    mediaLink = featured_media.link
                    mediaAlt = featured_media.alt
                    if mediaAlt == "":
                        mediaAlt = title

                    contentfulImageId = contentfulImage(mediaLink, mediaAlt)

                    thumbnail = {
                        "sys": {
                            "type": "Link",
                            "linkType": "Asset",
                            "id": contentfulImageId
                        }
                    }
                except Media.DoesNotExist:
                    print("No Featured Media for post {}".format(title))

                # Author
                try:
                    wpAuthor = Author.objects.get(id=post.author)

                    authorName = html.unescape(wpAuthor.name)
                    authorSlug = wpAuthor.slug
                    authorDescription = self.cleanDescription(
                        wpAuthor.description)

                    contentfulAuthorId = contentfulAuthor(
                        authorName, authorSlug, authorDescription)

                    author = {
                        "sys": {
                            "type": "Link",
                            "linkType": "Entry",
                            "id": contentfulAuthorId
                        }
                    }
                except Media.DoesNotExist:
                    print("No Featured Media for post {}".format(title))

                # Categories
                categories = []

                for categoryId in post.categories.split(','):
                    if categoryId != "":
                        try:

                            wpCategory = Category.objects.get(id=categoryId)

                            categoryName = html.unescape(wpCategory.name)
                            categorySlug = wpCategory.slug
                            categoryDescription = self.cleanExcerpt(
                                wpCategory.description)

                            contentfulCategoryId = contentfulCategory(
                                categoryName, categorySlug, categoryDescription)

                            categories.append({
                                "sys": {
                                    "type": "Link",
                                    "linkType": "Entry",
                                    "id": contentfulCategoryId
                                }
                            })

                        except Media.DoesNotExist:
                            print("No Featured Media for post {}".format(title))

                # Tags
                tags = []

                for tagId in post.tags.split(','):
                    if tagId != "":
                        try:
                            wpTag = Tag.objects.get(id=tagId)

                            tagName = html.unescape(wpTag.name)
                            tagSlug = wpTag.slug
                            tagDescription = self.cleanExcerpt(
                                wpTag.description)

                            contentfulTagId = contentfulTag(
                                tagName, tagSlug, tagDescription)

                            tags.append({
                                "sys": {
                                    "type": "Link",
                                    "linkType": "Entry",
                                    "id": contentfulTagId
                                }
                            })

                        except Media.DoesNotExist:
                            print("No Tag for post {}".format(title))

                # Create Post
                contentfulPost(title, slug, body, seoTitle, seoDescription,
                               date, thumbnail, author, categories, tags)

                print("--------------------------------------------------------")

            except Exception as e:
                print(e)
                continue
