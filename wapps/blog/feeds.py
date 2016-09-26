from urllib import parse

from wapps.feed import SiteFeed
from wapps.utils import get_image_url


class BlogFeed(SiteFeed):
    def __init__(self, blog, *args, **kwargs):
        self.blog = blog
        super().__init__(*args, **kwargs)

    def __call__(self, request, *args, **kwargs):
        kwargs['page'] = self.blog
        return super().__call__(request, *args, **kwargs)

    def title(self):
        return self.meta.full_title

    def description(self):
        return self.meta.description

    subtitle = description

    def link(self):
        return self.blog.full_url

    def items(self):
        return self.blog.get_queryset()[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.body

    def item_pubdate(self, item):
        return item.date

    def item_link(self, item):
        return item.full_url

    def item_enclosure_url(self, item):
        if item.image:
            image_url = get_image_url(item.image, 'original')
            return parse.urljoin(self.site.root_url, image_url)

    def item_enclosure_mime_type(self, item):
        if item.image:
            return 'image/png'

    def item_enclosure_length(self, item):
        if item.image:
            return 0

    def item_content(self, item):
        return str(item.body)