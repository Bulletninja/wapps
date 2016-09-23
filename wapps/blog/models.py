from datetime import date, datetime

from django.db import models
from django.utils.dateformat import DateFormat
from django.utils.formats import date_format
from django.utils.functional import cached_property
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import TaggedItemBase
from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin, route
from wagtail.wagtailcore import blocks
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index
from wagtail.utils.pagination import paginate

from wapps.models import Category
from wapps.mixins import RelatedLink
from wapps.utils import get_image_model

from .feeds import BlogRssFeed, BlogAtomFeed

ImageModel = get_image_model()

DEFAULT_PAGE_SIZE = 10


def get_common_context(context):
    context['blog_tags'] = BlogPostTag.tags_for(BlogPost).annotate(
        item_count=models.Count('taggit_taggeditem_items')
    ).order_by('-item_count')
    context['all_categories'] = Category.objects.all()
    context['root_categories'] = Category.objects.filter(
        parent=None,
    ).prefetch_related(
        'children',
    ).annotate(
        blog_count=models.Count('blogpost'),
    )
    return context


class Blog(RoutablePageMixin, Page):
    '''
    A blog root page handling article querying and listing
    '''
    intro = RichTextField(blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
    ]

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('intro', classname="full"),
    ]

    promote_panels = Page.promote_panels

    def get_queryset(self):
        # Get list of live blog posts that are descendants of this page
        qs = BlogPost.objects.live().descendant_of(self)

        # Order by most recent date first
        qs = qs.order_by('-first_published_at')

        return qs

    def get_context(self, request):
        context = super(Blog, self).get_context(request)

        _, posts = paginate(request, self.posts, 'page', DEFAULT_PAGE_SIZE)
        context['posts'] = posts
        context = get_common_context(context)
        return context

    @route(r'^$')
    def all_posts(self, request, *args, **kwargs):
        self.posts = self.get_queryset()
        return Page.serve(self, request, *args, **kwargs)

    @route(r'^(\d{4})/$')
    @route(r'^(\d{4})/(\d{2})/$')
    @route(r'^(\d{4})/(\d{2})/(\d{2})/$')
    def by_date(self, request, year, month=None, day=None, *args, **kwargs):
        self.posts = self.get_queryset().filter(first_published_at__year=year)
        self.filter_type = _('date')
        self.filter_term = year
        if month:
            self.posts = self.posts.filter(date__month=month)
            df = DateFormat(date(int(year), int(month), 1))
            self.filter_term = df.format('F Y')
        if day:
            self.posts = self.posts.filter(date__day=day)
            self.filter_term = date_format(date(int(year), int(month), int(day)))
        return Page.serve(self, request, *args, **kwargs)

    @route(r'^tag/(?P<tag>[-\w]+)/$')
    def by_tag(self, request, tag, *args, **kwargs):
        self.filter_type = _('tag')
        self.filter_term = tag
        self.posts = self.get_queryset().filter(tags__slug=tag)
        return Page.serve(self, request, *args, **kwargs)

    @route(r'^category/(?P<category>[-\w]+)/$')
    def by_category(self, request, category, *args, **kwargs):
        self.filter_type = _('category')
        self.filter_term = category
        self.posts = self.get_queryset().filter(blogpost_categories__category__slug=category)
        return Page.serve(self, request, *args, **kwargs)

    @route(r'^author/(?P<author>\w+)/$')
    def by_author(self, request, author, *args, **kwargs):
        self.filter_type = _('author')
        self.filter_term = author
        self.posts = self.get_queryset().filter(owner__username=author)
        return Page.serve(self, request, *args, **kwargs)

    @route(r'^rss/$')
    def rss(self, request, *args, **kwargs):
        feed = BlogRssFeed()
        kwargs['blog'] = self
        return feed(request, *args, **kwargs)

    @route(r'^atom/$')
    def atom(self, request, *args, **kwargs):
        feed = BlogAtomFeed()
        kwargs['blog'] = self
        return feed(request, *args, **kwargs)

    subpage_types = ['blog.BlogPost']


class BlogPostRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('blog.BlogPost', related_name='related_links')


class BlogPostCategory(models.Model):
    category = models.ForeignKey(Category, related_name="+", verbose_name=_('Category'))
    page = ParentalKey('BlogPost', related_name='blogpost_categories')
    panels = [
        FieldPanel('category'),
    ]


class BlogPostTag(TaggedItemBase):
    content_object = ParentalKey('blog.BlogPost', related_name='tagged_items')


class BlogPost(Page):
    '''
    A single blog post (aka. article) page
    '''
    class Meta:
        verbose_name = _('Blog post')
        verbose_name_plural = _('Blog posts')

    body = RichTextField(verbose_name=_('body'))
    excerpt = RichTextField(verbose_name=_('excerpt'), blank=True,
                            help_text=_("Entry excerpt to be displayed on entries list. "
                                        "If this field is not filled, a truncate version of body text will be used."))

    date = models.DateTimeField(verbose_name=_("Post date"), default=datetime.today)

    tags = ClusterTaggableManager(through=BlogPostTag, blank=True)
    categories = models.ManyToManyField(Category, through=BlogPostCategory, blank=True)

    image = models.ForeignKey(
        ImageModel,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.SearchField('excerpt'),
        index.FilterField('page_ptr_id')
    ]

    content_panels = [
        MultiFieldPanel([
            FieldPanel('title', classname="title"),
            ImageChooserPanel('image'),
            FieldPanel('body', classname="full"),
            FieldPanel('excerpt', classname="full"),
        ], heading=_('Content')),
        MultiFieldPanel([
            FieldPanel('tags'),
            InlinePanel('blogpost_categories', label=_('Categories')),
            InlinePanel('related_links', label=_('Related links')),
        ], heading=_('Metadata')),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('date'),
        FieldPanel('owner'),
    ]
    #  settings_panels = [
    #     MultiFieldPanel([
    #         FieldRowPanel([
    #             FieldPanel('go_live_at'),
    #             FieldPanel('expire_at'),
    #         ], classname="label-above"),
    #     ], 'Scheduled publishing', classname="publishing"),
    #     FieldPanel('date'),
    #     FieldPanel('author'),
    # ]

    parent_page_types = ['blog.Blog']
    subpage_types = []
    type_icon = 'fa-rss-square'

    @property
    def blog(self):
        # Find closest ancestor which is a blog index
        return self.get_ancestors().type(Blog).last().specific

    # @property
    # def date(self):
    #     return self.first_published_at

    def get_context(self, request):
        context = super(BlogPost, self).get_context(request)
        context = get_common_context(context)
        return context

    def summarize(self, length=255):
        text = self.excerpt or self.search_description or self.body
        return Truncator(strip_tags(str(text))).chars(length)

    def __jsonld__(self, context):
        request = context['request']
        data = {
            '@context': 'http://schema.org',
            '@type': 'BlogPosting',
            '@id': self.full_url,
            'name': self.seo_title or self.title,
            'datePublished': self.first_published_at.isoformat(),
            'dateModified': self.latest_revision_created_at.isoformat(),
            'headline': self.summarize(100),
            'articleBody': str(self.body),
            'author': {
                '@type': 'Person',
                'name': self.owner.get_full_name()
            },
        }
        if self.image:
            data['image'] = request.site.root_url + self.image.get_rendition('original').url
        return data

BlogPost._meta.get_field('owner').editable = True


class BlogBlock(blocks.PageChooserBlock):
    @cached_property
    def target_model(self):
        return Blog

    def get_context(self, value):
        context = super(BlogBlock, self).get_context(value)
        context['blog'] = context['value']
        return context

    class Meta:
        label = _('Blog')
        icon = 'fa-newspaper-o'
        # template = 'sublime/blocks/blog-section.html'
