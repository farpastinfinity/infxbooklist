from django.db import models
from django.forms import ValidationError
from django.contrib.auth.models import User
from settings import AMAZON_KEY, BOOK_COVERS
from utils import english_list
from django.forms import ModelForm
import ecs
import urllib2
import pyisbn
import os


class ISBNField(models.CharField):
    def __init__(self, **kwargs):
        kwargs['max_length'] = 13
        super(ISBNField, self).__init__(**kwargs)
    def get_internal_type(self):
        return 'CharField'
    def clean(self, value):
        value = super(ISBNField, self).clean(value)
        value = ''.join(value.split('-'))
        try:
            if not pyisbn.validate(value):
                raise ValidationError('Invalid ISBN')
        except (TypeError, ValueError), e:
            raise ValidationError, str(e)
        return value


class Book(models.Model):
    gid = models.CharField('Google Books ID', max_length=30, unique=True)
    isbn = ISBNField(null=True)
    title = models.CharField(max_length=200)
    authors = models.CharField(max_length=200)
    cover_image = models.FilePathField(path=BOOK_COVERS)
    added = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return u'"%s" by %s' % (self.title, self.authors)
    def url(self):
        return 'http://books.google.com/books?id='+self.gid
    def get_comments(self):
        return [r for r in self.recommendation_set.all() if r.comment]
    def get_silent_recommendations(self):
        return [r for r in self.recommendation_set.all() if not r.comment]
    def get_all_recommendations(self):
        return [r for r in self.recommendation_set.all()]
           
class Category(models.Model):
    class Meta:
        verbose_name_plural = "categories"
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=50, unique=True)
    books = models.ManyToManyField(Book, null=True, blank=True)
    category_type = models.ForeignKey('CategoryType')
    def __unicode__(self):
        return self.name
    #TODO: turn following into permalink
    def get_absolute_url(self):
        return "/%i/" % self.slug


class CategoryType(models.Model):
    """
    A category of categories, so to speak.
    This is largely to group categories
    on the index page by, say, whether
    they describe the audience or subject
    matter.
    """
    description = models.CharField(max_length=64)
    def get_categories(self):
        return self.category_set.all()
    def __unicode__(self):
        return self.description


class Recommendation(models.Model):
    user = models.ForeignKey(User)
    book = models.ForeignKey(Book)
    added = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    comment = models.TextField(blank=True)
    def __unicode__(self):
        if self.comment:
            return self.book.authors[:7]+": "+str(self.user)+": "+self.comment[:20]
        else:
            return u"<Blank recommendation by %s>" % unicode(self.user)


class FeedbackNote(models.Model):
    """A note left by a user."""
    text = models.TextField()
    def __unicode__(self):
        return self.text[:100]

# This model creates a profile attacked to each user that stores a picture and a URL
class UserProfile(models.Model):
	user = models.ForeignKey(User, unique=True, related_name='profile')
	picture = models.ImageField(upload_to='pictures', blank=True)
	site = models.CharField(max_length=100, blank=True)
	def __unicode__(self):
		return self.user.username

# This allows for easy creation of the HTML form used to edit the profile information
class ProfileForm(ModelForm):
	class Meta:
		model = UserProfile
		exclude = ('user')

# This will create a user profile if one does not exist when a profile field is accessed
User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


