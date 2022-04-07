from django.core.management.base import BaseCommand

import requests
import json
from bs4 import BeautifulSoup

from library.contentful import contentfulImage, contentfulCTA, contentfulPost, contentfulTable, contentfulScorecard, contentfulEmbed, contentfulAffiliate, contentfulAuthor, contentfulCategory, contentfulTag


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
        latestH3 = ""

        contents = []
        for element in elements:
            if element.name == 'h1':
                content = {
                    "data": {},
                    "content": [
                        {
                            "data": {},
                            "marks": [],
                            "value": element.string.strip(),
                            "nodeType": "text"
                        }
                    ],
                    "nodeType": "heading-1"
                }

                contents.append(content)

            if element.name == 'h2':
                content = {
                    "data": {},
                    "content": [
                        {
                            "data": {},
                            "marks": [],
                            "value": element.string.strip(),
                            "nodeType": "text"
                        }
                    ],
                    "nodeType": "heading-2"
                }

                contents.append(content)

            if element.name == 'h3':
                if element.has_attr('class') and 'elementor-cta__title' in element['class']:
                    continue

                if "The Latest" in element.string and "Reviews:" in element.string:
                    continue

                content = {
                    "data": {},
                    "content": [
                        {
                            "data": {},
                            "marks": [],
                            "value": element.string.strip(),
                            "nodeType": "text"
                        }
                    ],
                    "nodeType": "heading-3"
                }

                contents.append(content)

                latestH3 = element.string.strip()

            if element.name == 'h4':
                if element.has_attr('class') and 'elementor-toc__header-title' in element['class']:
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
                            "value": element.string.strip(),
                            "nodeType": "text"
                        }
                    ],
                    "nodeType": "heading-4"
                }

                contents.append(content)

            if element.name == 'p':
                parent = element.parent
                if parent.has_attr('class') and 'elementor-post__excerpt' in parent['class']:
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
                ulContents = []
                for child in element.children:
                    liContents = []
                    for grandchild in child.children:
                        if grandchild.name != None and len(grandchild.find_all('a')) > 0:
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
                olContents = []
                for child in element.children:
                    liContents = []
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

        return soup.get_text().strip()

    def main(self):

        print('Collecting All posts data...')

        allPosts = []
        for page in range(1, 5):
            print("Page {}".format(page))

            postsRes = requests.request(
                "GET", "https://www.americanfirearms.org/wp-json/wp/v2/posts?per_page=100&page={}".format(page), headers={}, data={})

            posts = json.loads(postsRes.text)

            for post in posts:
                allPosts.append(post)

        print('Uploading posts to Contentful...')

        for post in allPosts:
            try:
                print("--------------------------------------------------------")

                # Main
                title = post['title']['rendered'].replace(
                    '&amp;', '&').strip()
                slug = post['slug']
                body = self.convertHTMLToContentfulJson(
                    post['content']['rendered'])
                excerpt = self.cleanExcerpt(post['excerpt']['rendered'])
                date = post['date']

                # Thumbnail
                featuredMediaLink = post['_links']['wp:featuredmedia'][0]['href']
                featuredMediaRes = requests.request(
                    "GET", featuredMediaLink, headers={}, data={})
                featuredMediaData = json.loads(featuredMediaRes.text)

                imageLink = featuredMediaData['source_url']
                imageAlt = featuredMediaData['alt_text']
                if imageAlt == "":
                    imageAlt = title

                thumbnail = {
                    "sys": {
                        "type": "Link",
                        "linkType": "Asset",
                        "id": contentfulImage(imageLink, imageAlt)
                    }
                }

                # Author
                authorLink = post['_links']['author'][0]['href']
                authorRes = requests.request(
                    "GET", authorLink, headers={}, data={})
                authorData = json.loads(authorRes.text)

                author = {
                    "sys": {
                        "type": "Link",
                        "linkType": "Entry",
                        "id": contentfulAuthor(
                                authorData['name'], authorData['slug'], authorData['description'])
                    }
                }

                # Categories
                categoriesLink = post['_links']['wp:term'][0]['href']
                categoriesRes = requests.request(
                    "GET", categoriesLink, headers={}, data={})
                categoriesData = json.loads(categoriesRes.text)

                categories = []
                for categoryData in categoriesData:
                    categorySlug = categoryData['slug']
                    categoryName = categoryData['name'].replace(
                        '&amp;', '&')
                    categoryDescription = categoryData['description']

                    category = contentfulCategory(
                        categoryName, categorySlug, categoryDescription)

                    categories.append({
                        "sys": {
                            "type": "Link",
                            "linkType": "Entry",
                            "id": category
                        }
                    })

                # Tags
                tagsLink = post['_links']['wp:term'][1]['href']
                tagsRes = requests.request(
                    "GET", tagsLink, headers={}, data={})
                tagsData = json.loads(tagsRes.text)

                tags = []
                for tagData in tagsData:
                    tagSlug = tagData['slug']
                    tagName = tagData['name'].replace('&amp;', '&')
                    tagDescription = tagData['description']

                    tag = contentfulTag(
                        tagName, tagSlug, tagDescription)

                    tags.append({
                        "sys": {
                            "type": "Link",
                            "linkType": "Entry",
                            "id": tag
                        }
                    })

                # Create Post
                contentfulPost(title, slug, body, excerpt,
                               date, thumbnail, author, categories, tags)

                print("--------------------------------------------------------")

            except Exception as e:
                print(e)
                continue
