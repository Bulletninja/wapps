import jinja2

from django.utils.html import strip_tags

from django_jinja import library

from wapps.models import IdentitySettings
from wapps.utils import get_image_url


class Metadata(object):
    '''
    Extract metadata from a Page object
    '''
    def __init__(self, context=None, **kwargs):
        self.context = context or {}
        self.kwargs = kwargs
        self.request = kwargs.get('request', None) or context.get('request', None)
        self.page = kwargs.get('page', None) or context.get('page', None)
        self.site = kwargs.get('site', None) or self.request.site
        self.identity = IdentitySettings.for_site(self.site)

    @property
    def title(self):
        if self.kwargs.get('title'):
            return self.kwargs['title']
        elif self.page:
            return self.page.seo_title or self.page.title

    @property
    def site_title(self):
        return self.identity.name or self.context.get('WAGTAIL_SITE_NAME')

    @property
    def full_title(self):
        if self.site_title and self.title:
            return ' | '.join((self.title, self.site_title))
        elif self.site_title:
            return self.site_title
        elif self.title:
            return self.title

    @property
    def description(self):
        if self.kwargs.get('description'):
            return self.kwargs['description']
        elif getattr(self.page, 'search_description', None):
            return self.page.search_description
        elif getattr(self.page, 'excerpt', None):
            return self.page.excerpt
        elif getattr(self.page, 'intro', None):
            return strip_tags(self.page.intro)
        elif getattr(self.page, 'description', None):
            return strip_tags(self.page.description)
        else:
            return self.identity.description

    @property
    def image(self):
        if self.kwargs.get('image'):
            return self.kwargs['image']
        elif getattr(self.page, 'feed_image', None):
            return self.page.feed_image
        elif getattr(self.page, 'image', None):
            return self.page.image
        elif self.identity.logo:
            return self.identity.logo

    @property
    def image_url(self):
        if self.kwargs.get('image_url'):
            return self.kwargs['image_url']
        elif self.image:
            return self.site.root_url + get_image_url(self.image, 'original')

    @property
    def tags(self):
        tags = set(self.identity.tags.all())
        if self.kwargs.get('tags'):
            tags.update(self.kwargs['tags'])
        if getattr(self.page, 'tags', None):
            tags.update(self.page.tags.all())
        return tags


@library.global_function
@jinja2.contextfunction
def page_meta(context, **kwargs):
    return Metadata(context, **kwargs)
