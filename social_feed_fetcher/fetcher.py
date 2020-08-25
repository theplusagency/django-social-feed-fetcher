from django.core.cache import cache
import requests

from social_feed_fetcher.exceptions import SocialFeedFetcherException
from social_feed_fetcher.signals import social_feed_fetch_failed


class BaseSocialFeedFetcher:
    # cache_timeout
    # Cache duration in seconds
    # Can be passed optionally as a parameter on initialization

    # With Async Cache Update configured, cache_duration can be set
    # to a high value (86400), so the posts stay available if the API
    # fetch action fail.

    # If you don't have Async Cache Update, then it's value will define
    # how often the posts will be fetched.
    cache_timeout = 3600

    # fail_silently
    # Don't raise any exceptions in case of failure
    # If the action of fetching posts fails, and fail_silently
    # is set to True, no exception will be raised.
    fail_silently = False

    def __init__(self, **kwargs):
        if 'cache_duration' in kwargs:
            self.cache_duration = kwargs.get('cache_duration')

        if 'fail_silently' in kwargs:
            self.fail_silently = kwargs.get('fail_silently')

    def get_feed(self):
        cached_feed = cache.get(self.get_cache_key(), None)

        if cached_feed:
            return cached_feed

        return self.update_feed()

    def get_cache_key(self):
        raise NotImplementedError

    def fetch_feed(self):
        raise NotImplementedError

    def update_feed(self):
        try:
            feed = self.fetch_feed()
            cache.set(self.get_cache_key(), feed, timeout=self.cache_timeout)

            return feed
        except Exception as exception:
            # Send custom social_feed_fetch_failed Django signal
            social_feed_fetch_failed.send(sender=self.__class__, exception=exception)

            if self.fail_silently:
                return []

            raise exception


class InstagramFeedFetcher(BaseSocialFeedFetcher):
    access_token = None
    username = None
    posts_to_fetch = 9

    def __init__(self, access_token, username, fail_silently=False):
        super().__init__(fail_silently=fail_silently)

        self.access_token = access_token
        self.username = username
        self.fail_silently = fail_silently

    def get_cache_key(self):
        return 'django-social-feed-fetcher-instagram-{}'.format(self.username)

    def fetch_feed(self):
        payload = {
            'fields': 'id,caption,media_type,media_url,permalink,thumbnail_url',
            'access_token': self.access_token,
            'limit': '{}'.format(self.posts_to_fetch)
        }

        response = (requests.get('https://graph.instagram.com/me/media', params=payload)).json()

        if not response or 'data' not in response.keys():
            raise SocialFeedFetcherException('Error fetching Instagram latest media')

        items = response['data']

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
