from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.views import redirect_to_login
from django.views.generic.list_detail import object_list
from models import Book, Category, CategoryType, FeedbackNote, Recommendation, User
from settings import AMAZON_KEY, DEBUG, BOOK_COVERS
from booklistapp.utils import english_list
from infxbooklist.booklistapp.models import ProfileForm
from django.template import RequestContext
from django.conf import settings
from django.contrib.auth import logout
import urllib
import urllib2
import ecs
import random
import os
import sys
import datetime
import gbooks
import json


class StringChunker:
    '''
    A dirty trick. This wraps a str
    and adds a generator 'chunks()' such
    that it can be passed to Django's
    File.save_image.
    '''
    def __init__(self, s):
        self.inner = s
    def chunks(self):
        yield self.inner
    def __getattr__(self, name):
        return getattr(self.inner, name)


def index(request, category):
    if not (request.user.is_authenticated()):
        isauth = False
    else:
        isauth = True
    sitename = settings.SITE_NAME
    sitedesc = settings.SITE_DESCRIPTION

    # What books to display
    if category:
        if category[-1] == '/':
            category = category[:-1]
        category_s = get_object_or_404(Category, slug=category)
        books_to_display = category_s.books.all().order_by('-edited')
        page_title = category_s.name
    else:
        books_to_display = Book.objects.all().order_by('-edited')
        
	if request.GET.get('r'):
		recommender = User.objects.get(username=request.GET.get('r'))
		recommendations = Recommendation.objects.all().filter(user=recommender.id)
		books_to_display.filter(recommendation__in=recommendations)
    qs = Recommendation.objects.values('user').order_by('user').distinct('user')
    users = User.objects.filter(id__in=qs).order_by('last_name','first_name','username')
    
    # Finish and render
    return object_list(request, queryset=books_to_display,
                       template_object_name='book',
                       paginate_by=100,
                       extra_context={'sitename': sitename,
                       					'sitedesc':sitedesc,
                                      'category_types': CategoryType.objects.all(),
                                      'recommenders': users,
                                      'current_slug': category,
                                      'isauth' : isauth })
def updateprofile(request):
	# Require login.
	if not (request.user.is_authenticated()):
		return redirect_to_login(request.get_full_path())
	profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)		
	request.user.first_name=request.POST['first_name']
	request.user.last_name=request.POST['last_name']
	request.user.email=request.POST['email']
	request.user.save()

	if profile_form.is_valid():
		profile_form.save()
	else:
		profile_form = ProfileForm(instance=request.user.profile)
	return HttpResponseRedirect("/edit/")

def update(request):
	# Require login.
	if not (request.user.is_authenticated()):
		return redirect_to_login(request.get_full_path())
		
	# Make sure gid is in the post request
	if not ('gid' in request.POST):
		return HttpResponseRedirect("/edit/")
		
	b = Book.objects.get(gid=request.POST['gid'])
	r = Recommendation.objects.get(user=request.user, book=b)
	for c in Category.objects.all():
		if c.slug in request.POST:
			c.books.add(b)
		else:
			c.books.remove(b)
	r.comment = request.POST['blurb']
	r.save()
	return HttpResponseRedirect('/edit/')

def delete(request):
    # Require login.
	if not (request.user.is_authenticated()):
		return redirect_to_login(request.get_full_path())
		
	# Make sure gid is in the post request
	if not ('gid' in request.POST):
		return HttpResponseRedirect("/edit/")
	
	# Get users recommendation for some gid
	book = Book.objects.get(gid=request.POST['gid'])
	try:
		rec = Recommendation.objects.get(user=request.user, book=book)
		rec.delete()
		if len(Recommendation.objects.filter(book=rec.book)) == 0:
			path = os.path.join(BOOK_COVERS, rec.book.cover_image)
			os.unlink(path)
			
			rec.book.delete()
	except Recommendation.DoesNotExist:
		return HttpResponseRedirect("/edit/")
	except:
		raise	
	
	return HttpResponseRedirect("/edit/")
	
def add(request):
	# Require login.
	if not (request.user.is_authenticated()):
		return redirect_to_login(request.get_full_path())
		
	# Make sure gid is in the post request
	if not ('gid' in request.POST):
		return HttpResponseRedirect("/edit/")
	
	try:
		b = Book.objects.get(gid=request.POST['gid'])
	except Book.DoesNotExist:
		# Book being recommended doesn't already exist, so add it.
		b = Book.objects.create(gid=request.POST['gid'])
		gb = gbooks.get(request.POST['gid'])
		b.title = gb.title
		b.authors = gb.authors
		b.isbn = gb.isbn
		try:
			# Download the thumbnail image from Google
			req = urllib2.Request(gb.thumbnail_url)
			req.add_header("User-Agent", "Mozilla")
			try:
				image_link = urllib2.urlopen(req)
				img_data = image_link.read()
				image_link.close()
				rand_fn = b.isbn + '-' + b.gid
				rand_pth = os.path.join(BOOK_COVERS, rand_fn)
				with open(rand_pth, 'w') as f:
					os.chmod(rand_pth, 0666)
					f.write(img_data)
				b.cover_image = rand_fn
			except Exception, e:
				print >>sys.stderr, "Tried to save thumbnail, but got exception:", repr(e)
		finally:
			b.save()
	# Now add the recommendation
	try:
		recommendation = Recommendation.objects.get(user=request.user, book=b)
	except Recommendation.DoesNotExist:
		recommendation = Recommendation.objects.create(user=request.user, book=b)
	finally:
		recommendation.save()
	return HttpResponseRedirect("/edit/")

def edit(request):    
	# Require login.
	if not (request.user.is_authenticated()):
		return redirect_to_login(request.get_full_path())
			
	recs = Recommendation.objects.filter(user=request.user).order_by('-added')
	category_types = CategoryType.objects.all()
	all_categories = Category.objects.all()
	context = {'recs': recs,
               'category_types': category_types,
               'user': request.user,
               'cat_check_htmls': []}
	books_in_c = {}
	for c in all_categories:
		books_in_c[c] = [r for r in recs.filter(book__category=c) \
                                        .distinct()]
	print >>sys.stderr, repr(books_in_c)
	for rec in recs:
		b = ''
		for ct in category_types:
			b += '<h4>%s</h4>' % ct.description
			for c in ct.get_categories():
				b += '<span class="checkbox-container"><input class="form-update-checkbox-' + rec.book.gid +'" type="checkbox" name="{0}" id="{1}{0}"'.format(c.slug, rec.id)
				if rec in books_in_c[c]:
					b += 'checked="checked" '
				b += '/><label for="%d%s">%s</label></span>' % (rec.id, c.slug, c.name)
		context['cat_check_htmls'].insert(0,b)
             
	if 'keywords' in request.GET:
		context['results'] = gbooks.search(request.GET['keywords'])
	elif 'gid' in request.POST:
		if 'action' in request.POST:
			if request.POST['action'] == 'update':
				b = Book.objects.get(gid=request.POST['gid'])
				r = Recommendation.objects.get(user=request.user,
											   book=b)
				for c in Category.objects.all():
					if c.slug in request.POST:
						c.books.add(b)
					else:
						c.books.remove(b)
				r.comment = request.POST['blurb']
				r.save()
				print >>sys.stderr, repr(request.POST)
			elif request.POST['action'] == 'delete':
				b = Book.objects.get(gid=request.POST['gid'])
				r = Recommendation.objects.get(user=request.user,
											   book=b)
				if len(Recommendation.objects.filter(book=r.book)) == 1:
					os.unlink(os.path.join(BOOK_COVERS, r.book.cover_image))
					r.book.delete()
				r.delete()
			# Redirect to avoid refresh issues
			return HttpResponseRedirect("/edit/")
	elif 'profileaction' in request.POST:
		if request.POST['profileaction'] == 'update':
			profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
			
			request.user.first_name=request.POST['first_name']
			request.user.last_name=request.POST['last_name']
			request.user.email=request.POST['email']
			request.user.save()

			if profile_form.is_valid():
				profile_form.save()
				return HttpResponseRedirect('/edit/')

			else:
				profile_form = ProfileForm(instance=request.user.profile)
				return HttpResponseRedirect('/edit/')

			#return render_to_response('edit.html', { 'form' : profile_form })
	profile_form = ProfileForm(instance=request.user.profile)
	# Go.
	context['form'] = profile_form
	if request.user.profile.picture:
		context['pictureurl'] = request.user.profile.picture.url
	context['siteurl'] = request.user.profile.site
	context['firstname'] = request.user.first_name
	context['lastname'] = request.user.last_name
	context['email'] = request.user.email
	context['sitename'] = settings.SITE_NAME
	return render_to_response('edit.html', context, context_instance=RequestContext(request))

def profile(request):
	if request.method == 'POST':
		profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

		if profile_form.is_valid():
			profile_form.save()
			return HttpResponseRedirect('/profile/')

		else:
			profile_form = ProfileForm(instance=request.user.profile)

		return render_to_response('profile.html', { 'form' : profile_form })
	else:
		profile_form = ProfileForm(instance=request.user.profile)
		return render_to_response('profile.html', { 'form' : profile_form, 'test' : request.user.profile.site, 'blah' : request.user.profile.picture.url }, context_instance=RequestContext(request))

def logout(request):
	logout(request)
	return redirect('booklistapp.views.index')

def feedback(request):
    if 'text' in request.POST:
        f = FeedbackNote(text=request.POST['text'])
        f.save()
        return HttpResponse(status=200)
    return HttpResponse(status=400)