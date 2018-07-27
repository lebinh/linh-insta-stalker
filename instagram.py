from __future__ import division

import time
from pprint import pprint

import humanize
import requests


class User(object):
    def __init__(self, username):
        if not username:
            raise ValueError('username cannot be empty')
        if username.startswith('@'):
            username = username.lstrip('@')
        self.username = username
        self._loaded = False
        self.data = None
        self.recent_posts = None

    def load(self):
        url = 'https://www.instagram.com/{}/?__a=1'.format(self.username)
        resp = requests.get(url)
        if resp.status_code == 404:
            raise ValueError("user not found: {}".format(self.username))
        print(self.username)
        print(url)
        print(resp.text)
        self.data = resp.json()
        self.recent_posts = [Post(data['node']) for data in self.data['graphql']['user']['edge_owner_to_timeline_media']['edges']]
        self._loaded = True

    def __repr__(self):
        return '<User username={}>'.format(self.username)

    def _require_load(self):
        if not self._loaded:
            self.load()

    def _require_recent_posts(self):
        if not self._loaded:
            self.load()
        if self.is_private:
            raise ValueError('user is private')
        if not self.recent_posts:
            raise ValueError('no recent posts found')

    @property
    def is_private(self):
        self._require_load()
        return self.data['graphql']['user']['is_private']

    @property
    def fullname(self):
        self._require_load()
        return self.data['graphql']['user']['full_name']

    @property
    def biography(self):
        self._require_load()
        return self.data['graphql']['user']['biography']

    @property
    def followers_count(self):
        self._require_load()
        return self.data['graphql']['user']['edge_followed_by']['count']

    @property
    def following_count(self):
        self._require_load()
        return self.data['graphql']['user']['edge_follow']['count']

    @property
    def posts_count(self):
        self._require_load()
        return self.data['graphql']['user']['edge_owner_to_timeline_media']['count']

    @property
    def average_likes_recently(self):
        self._require_recent_posts()
        return sum(p.likes_count for p in self.recent_posts) / len(self.recent_posts)

    @property
    def average_comments_recently(self):
        self._require_recent_posts()
        return sum(p.comments_count for p in self.recent_posts) / len(self.recent_posts)

    @property
    def engagement_rate(self):
        self._require_recent_posts()
        return (self.average_comments_recently + self.average_likes_recently) / self.followers_count * 100

    @property
    def average_seconds_between_posts(self):
        self._require_recent_posts()
        deltas = [self.recent_posts[i + 1].created_time - self.recent_posts[i].created_time
                  for i in range(len(self.recent_posts) - 1)]
        return sum(abs(d) for d in deltas) / len(deltas)

    def report(self):
        time_between_posts = humanize.naturaldelta(self.average_seconds_between_posts)
        time_since_last_post = humanize.naturaldelta(time.time() - self.recent_posts[0].created_time)
        return ('@{0.username} ({0.fullname}) has {0.followers_count} followers and '
                'about {0.engagement_rate:.1f}% engagement rate.\n'
                'He/she has posted {0.posts_count} times with an average of '
                '{0.average_likes_recently:.1f} likes and {0.average_comments_recently:.1f} comments'
                'per post recently.\n'
                'There is about {1} between his/her posts recently and the last post is {2} ago.'
                ).format(self, time_between_posts, time_since_last_post)


class Post(object):
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return '<Post code={}>'.format(self.data['code'])

    @property
    def comments_count(self):
        return self.data['edge_media_to_comment']['count']

    @property
    def likes_count(self):
        return self.data['edge_liked_by']['count']

    @property
    def is_video(self):
        return self.data.get('is_video', False)

    @property
    def video_views_count(self):
        return self.data.get('video_views', 0)

    @property
    def created_time(self):
        return self.data['date']
