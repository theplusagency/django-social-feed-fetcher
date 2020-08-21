from django.core.cache import cache
import requests

from social_feed_fetcher.signals import social_feed_fetch_failed


class BaseSocialFeedFetcher:
    fail_silently = False

    def __init__(self, fail_silently):
        self.fail_silently = fail_silently

    def get_feed(self):
        cached_feed = cache.get(self.get_cache_key())

        if cached_feed:
            return cached_feed

        return self.update_feed()

    def get_cache_key(self):
        raise NotImplementedError

    def fetch_feed(self):
        raise NotImplementedError

    def update_feed(self):
        try:
            return self.fetch_feed()
        except Exception as exception:
            social_feed_fetch_failed.send(sender=self.__class__, exception=exception)

            if self.fail_silently:
                return []

            raise exception


class InstagramSocialFeedFetcher(BaseSocialFeedFetcher):
    access_token = None
    username = None
    posts_to_fetch = 9

    def __init__(self, access_token, username, fail_silently=False):
        super().__init__(fail_silently)

        self.access_token = access_token
        self.username = username
        self.fail_silently = fail_silently

    def get_cache_key(self):
        return 'django-social-feed-fetcher-instagram-{}'.format(self.username)

    def fetch_feed(self):
        payload = {
            'fields': 'id,caption,media_type,media_url,permalink,thumbnail_url',
            'access_token': self.access_token,
            'limit': '9'
        }

        response = (requests.get('https://graph.instagram.com/me/media', params=payload)).json()

        items = []

        for media in response['data']:
            items.append({
                'image': media['thumbnail_url'] if media['media_type'] == 'VIDEO' else media['media_url'],
                'link': media['permalink']
            })

        return items


# class FacebokSocialFeedFetcher:
#     access_token = None
#     username = None
#     fail_silently = False
#     posts_to_fetch = 1
# 
#     def __init__(self, access_token, username, fail_silently=False):
#         self.access_token = access_token
#         self.username = username
#         self.fail_silently = fail_silently
# 
#     def update_facebook_feed(pageid):
#         logger.info('Actualizando Facebook feed de {}'.format(pageid))
# 
#         graph = facebook.GraphAPI(
#             access_token=settings.SOCIAL_FEEDS_FACEBOOK_ACCESS_TOKEN,
#             version=settings.SOCIAL_FEEDS_FACEBOOK_GRAPH_API_VERSION)
#         feed = graph.get_object('{}/published_posts'.format(pageid), fields=FB_POST_FIELDS, limit=1)
#         feed_data = []
# 
#         post = feed['data'][0]
#         first_attachment = post['attachments']['data'][0]
# 
#         post_data = {}
# 
#         if first_attachment['type'] in ['video_inline', 'video', 'video_autoplay']:
#             post_data['type'] = 'video'
# 
#         post_data['image_url'] = post['full_picture']
#         post_data['link'] = first_attachment['target']['url']
# 
#         cache.set(get_facebook_feed_cache_key(pageid), [post_data], settings.SOCIAL_FEEDS_CACHE_DURATION)
# 
#         return [post_data]
