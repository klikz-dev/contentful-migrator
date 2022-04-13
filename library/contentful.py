from unicodedata import name
import requests
import json
import environ
import os
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


def uploadImage(link, alt, fileName=""):
    url = "https://api.contentful.com/spaces/{}/environments/{}/assets".format(
        env('CONTENTFUL_SPACE_ID'), env('CONTENTFUL_ENVIRONMENT_ID'))

    if fileName == "":
        fileName = link.split('/')[-1].replace('.jpg', '')

    if alt == "":
        alt = fileName

    payload = json.dumps({
        "fields": {
            "title": {
                "en-US": alt
            },
            "file": {
                "en-US": {
                    "contentType": "image/jpeg",
                    "fileName": fileName,
                    "upload": link
                }
            }
        }
    })

    headers = {
        'Authorization': 'Bearer {}'.format(env('CONTENTFUL_MANAGEMENT_TOKEN')),
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code != 201:
        print("Image creation failed. Link: {}, Alt: {}".format(link, alt))
        print(response.text)
        return None
    else:
        print("Image creation successful. Link: {}, Alt: {}".format(link, alt))
        return json.loads(response.text)


def processImage(imageId, version):
    url = "https://api.contentful.com/spaces/{}/environments/{}/assets/{}/files/en-US/process".format(
        env('CONTENTFUL_SPACE_ID'), env('CONTENTFUL_ENVIRONMENT_ID'), imageId)

    payload = {}

    headers = {
        'X-Contentful-Version': str(version),
        'Authorization': 'Bearer {}'.format(env('CONTENTFUL_MANAGEMENT_TOKEN')),
    }

    response = requests.request("PUT", url, headers=headers, data=payload)

    if response.status_code != 204:
        print("Image Process Error. Image: {}".format(imageId))
        print(response.text)


def publishImage(imageId, version):
    url = "https://api.contentful.com/spaces/{}/environments/{}/assets/{}/published".format(
        env('CONTENTFUL_SPACE_ID'), env('CONTENTFUL_ENVIRONMENT_ID'), imageId)

    payload = {}

    headers = {
        'X-Contentful-Version': str(version),
        'Authorization': 'Bearer {}'.format(env('CONTENTFUL_MANAGEMENT_TOKEN')),
    }

    response = requests.request("PUT", url, headers=headers, data=payload)

    if response.status_code != 200:
        print("Image Publish Error. Image: {}".format(imageId))
        print(response.text)


def publishEntry(entryId):
    url = "https://api.contentful.com/spaces/{}/environments/{}/entries/{}/published".format(
        env('CONTENTFUL_SPACE_ID'), env('CONTENTFUL_ENVIRONMENT_ID'), entryId)

    payload = {}

    headers = {
        'X-Contentful-Version': '1',
        'Authorization': 'Bearer {}'.format(env('CONTENTFUL_MANAGEMENT_TOKEN')),
    }

    response = requests.request("PUT", url, headers=headers, data=payload)

    if response.status_code != 200:
        print("Post Publish Error. Post: {}".format(entryId))
        print(response.text)


def contentfulImage(link, alt):
    upload = uploadImage(link, alt)
    if upload == None:
        return ""

    imageId = upload['sys']['id']
    version = upload['sys']['version']

    processImage(imageId, version)
    time.sleep(1)
    publishImage(imageId, version + 1)

    return imageId


def contentfulCTA(title, link, image, buttonText, price):
    url = "https://api.contentful.com/spaces/{}/environments/{}/entries".format(
        env('CONTENTFUL_SPACE_ID'), env('CONTENTFUL_ENVIRONMENT_ID'))

    payload = json.dumps({
        "fields": {
            "title": {
                "en-US": title
            },
            "link": {
                "en-US": link
            },
            "image": {
                "en-US": {
                    "sys": {
                        "type": "Link",
                        "linkType": "Asset",
                        "id": image
                    }
                }
            },
            "buttonText": {
                "en-US": buttonText
            },
            "price": {
                "en-US": float(str(price))
            }
        }
    })

    headers = {
        'X-Contentful-Content-Type': 'cta',
        'Authorization': 'Bearer {}'.format(env('CONTENTFUL_MANAGEMENT_TOKEN')),
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code != 201:
        print("Creating CTA failed")
        print(response.text)
        return ""

    else:
        print("CTA creation successful. Title: {}, Link: {}".format(title, link))
        cta = json.loads(response.text)

        publishEntry(cta['sys']['id'])
        return cta['sys']['id']


def contentfulTable(name, tableData, thumbnails):
    url = "https://api.contentful.com/spaces/{}/environments/{}/entries".format(
        env('CONTENTFUL_SPACE_ID'), env('CONTENTFUL_ENVIRONMENT_ID'))

    payload = json.dumps({
        "fields": {
            "name": {
                "en-US": name
            },
            "body": {
                "en-US": {
                    "tableData": tableData
                }
            },
            "images": {
                "en-US": thumbnails
            }
        }
    })

    headers = {
        'X-Contentful-Content-Type': 'table',
        'Authorization': 'Bearer {}'.format(env('CONTENTFUL_MANAGEMENT_TOKEN')),
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code != 201:
        print("Creating Table failed")
        print(response.text)
        return ""

    else:
        print("Table creation successful. Name: {}".format(name))
        table = json.loads(response.text)

        publishEntry(table['sys']['id'])
        return table['sys']['id']


def contentfulScorecard(name, tableData):
    url = "https://api.contentful.com/spaces/{}/environments/{}/entries".format(
        env('CONTENTFUL_SPACE_ID'), env('CONTENTFUL_ENVIRONMENT_ID'))

    payload = json.dumps({
        "fields": {
            "name": {
                "en-US": name
            },
            "body": {
                "en-US": {
                    "tableData": tableData
                }
            },
        }
    })

    headers = {
        'X-Contentful-Content-Type': 'scorecard',
        'Authorization': 'Bearer {}'.format(env('CONTENTFUL_MANAGEMENT_TOKEN')),
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code != 201:
        print("Creating Scorecard failed")
        print(response.text)
        return ""

    else:
        print("Scorecard creation successful. Name: {}".format(name))
        scorecard = json.loads(response.text)

        publishEntry(scorecard['sys']['id'])
        return scorecard['sys']['id']


def contentfulEmbed(src):
    url = "https://api.contentful.com/spaces/{}/environments/{}/entries".format(
        env('CONTENTFUL_SPACE_ID'), env('CONTENTFUL_ENVIRONMENT_ID'))

    payload = json.dumps({
        "fields": {
            "url": {
                "en-US": src
            }
        }
    })

    headers = {
        'X-Contentful-Content-Type': 'embed',
        'Authorization': 'Bearer {}'.format(env('CONTENTFUL_MANAGEMENT_TOKEN')),
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code != 201:
        print("Creating Embed failed")
        print(response.text)
        return ""

    else:
        print("Embed creation successful. Src: {}".format(src))
        embed = json.loads(response.text)

        publishEntry(embed['sys']['id'])
        return embed['sys']['id']


def contentfulAffiliate(productId):
    url = "https://api.contentful.com/spaces/{}/environments/{}/entries".format(
        env('CONTENTFUL_SPACE_ID'), env('CONTENTFUL_ENVIRONMENT_ID'))

    payload = json.dumps({
        "fields": {
            "productId": {
                "en-US": productId
            }
        }
    })

    headers = {
        'X-Contentful-Content-Type': 'amazonAffiliate',
        'Authorization': 'Bearer {}'.format(env('CONTENTFUL_MANAGEMENT_TOKEN')),
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code != 201:
        print("Creating Amazon Affiliate failed")
        print(response.text)
        return ""

    else:
        print("Amazon Affiliate creation successful. productId: {}".format(productId))
        amazonAffiliate = json.loads(response.text)

        publishEntry(amazonAffiliate['sys']['id'])
        return amazonAffiliate['sys']['id']


def contentfulAuthor(name, slug, description):
    url = "https://api.contentful.com/spaces/{}/environments/{}/entries?access_token={}&content_type={}&fields.slug={}".format(
        env('CONTENTFUL_SPACE_ID'), env('CONTENTFUL_ENVIRONMENT_ID'), env('CONTENTFUL_MANAGEMENT_TOKEN'), 'author', slug)

    response = requests.request("GET", url)

    authors = json.loads(response.text)

    if len(authors['items']) > 0:
        author = authors['items'][0]
        print("Existing Author. ID: {}".format(author['sys']['id']))
        return author['sys']['id']

    # New Author
    url = "https://api.contentful.com/spaces/{}/environments/{}/entries".format(
        env('CONTENTFUL_SPACE_ID'), env('CONTENTFUL_ENVIRONMENT_ID'))

    payload = json.dumps({
        "fields": {
            "name": {
                "en-US": name
            },
            "slug": {
                "en-US": slug
            },
            "description": {
                "en-US": description
            },
        }
    })

    headers = {
        'X-Contentful-Content-Type': 'author',
        'Authorization': "Bearer {}".format(env('CONTENTFUL_MANAGEMENT_TOKEN')),
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code != 201:
        print("Creating Author failed")
        print(response.text)
        return ""

    else:
        print("Author creation successful. Name: {}".format(name))
        author = json.loads(response.text)

        publishEntry(author['sys']['id'])
        return author['sys']['id']


def contentfulCategory(name, slug, description):
    url = "https://api.contentful.com/spaces/{}/environments/{}/entries?access_token={}&content_type={}&fields.slug={}".format(
        env('CONTENTFUL_SPACE_ID'), env('CONTENTFUL_ENVIRONMENT_ID'), env('CONTENTFUL_MANAGEMENT_TOKEN'), 'category', slug)

    response = requests.request("GET", url)

    categories = json.loads(response.text)

    if len(categories['items']) > 0:
        category = categories['items'][0]
        print("Existing Category. ID: {}".format(category['sys']['id']))
        return category['sys']['id']

    # New Category
    url = "https://api.contentful.com/spaces/{}/environments/{}/entries".format(
        env('CONTENTFUL_SPACE_ID'), env('CONTENTFUL_ENVIRONMENT_ID'))

    payload = json.dumps({
        "fields": {
            "name": {
                "en-US": name
            },
            "slug": {
                "en-US": slug
            },
            "description": {
                "en-US": description
            },
        }
    })

    headers = {
        'X-Contentful-Content-Type': 'category',
        'Authorization': "Bearer {}".format(env('CONTENTFUL_MANAGEMENT_TOKEN')),
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code != 201:
        print("Creating Category failed")
        print(response.text)
        return ""

    else:
        print("Category creation successful. Name: {}".format(name))
        category = json.loads(response.text)

        publishEntry(category['sys']['id'])
        return category['sys']['id']


def contentfulTag(name, slug, description):
    url = "https://api.contentful.com/spaces/{}/environments/{}/entries?access_token={}&content_type={}&fields.slug={}".format(
        env('CONTENTFUL_SPACE_ID'), env('CONTENTFUL_ENVIRONMENT_ID'), env('CONTENTFUL_MANAGEMENT_TOKEN'), 'tag', slug)

    response = requests.request("GET", url)

    tags = json.loads(response.text)

    if len(tags['items']) > 0:
        tag = tags['items'][0]
        print("Existing Tag. ID: {}".format(tag['sys']['id']))
        return tag['sys']['id']

    # New Tag
    url = "https://api.contentful.com/spaces/{}/environments/{}/entries".format(
        env('CONTENTFUL_SPACE_ID'), env('CONTENTFUL_ENVIRONMENT_ID'))

    payload = json.dumps({
        "fields": {
            "name": {
                "en-US": name
            },
            "slug": {
                "en-US": slug
            },
            "description": {
                "en-US": description
            },
        }
    })

    headers = {
        'X-Contentful-Content-Type': 'tag',
        'Authorization': "Bearer {}".format(env('CONTENTFUL_MANAGEMENT_TOKEN')),
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code != 201:
        print("Creating Tag failed")
        print(response.text)
        return ""

    else:
        print("Tag creation successful. Name: {}".format(name))
        tag = json.loads(response.text)

        publishEntry(tag['sys']['id'])
        return tag['sys']['id']


def contentfulPost(title, slug, body, excerpt, date, thumbnail, author, categories, tags):
    url = "https://api.contentful.com/spaces/{}/environments/{}/entries".format(
        env('CONTENTFUL_SPACE_ID'), env('CONTENTFUL_ENVIRONMENT_ID'))

    payload = json.dumps({
        "fields": {
            "title": {
                "en-US": title
            },
            "slug": {
                "en-US": slug
            },
            "body": {
                "en-US": body
            },
            "seo": {
                "en-US": excerpt
            },
            "publishedAt": {
                "en-US": date
            },
            "thumbnail": {
                "en-US": thumbnail
            },
            "author": {
                "en-US": author
            },
            "categories": {
                "en-US": categories
            },
            "tags": {
                "en-US": tags
            }
        }
    })

    headers = {
        'X-Contentful-Content-Type': 'post',
        'Authorization': 'Bearer {}'.format(env('CONTENTFUL_MANAGEMENT_TOKEN')),
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code != 201:
        print("Creating Post failed")
        print(response.text)
        return ""

    else:
        print("Post creation successful. Title: {}".format(title))
        post = json.loads(response.text)

        time.sleep(1)
        publishEntry(post['sys']['id'])
        return post['sys']['id']
