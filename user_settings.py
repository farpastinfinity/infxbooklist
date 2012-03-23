# Name of the site
# This value will show up on the header of every page
# Default: Informatics Booklist
# Try and keep this under 32 characters
SITE_NAME = 'Informatics Booklist'

# Description of the site
# This value will show up in gray at the top of the left sidebar.
# Feel free to be as descriptive as you like
SITE_DESCRIPTION = 'To give a better idea of what Informatics is all about, the faculty have recommended these books as particularly valuable or influential.'

# Site database
# By default, this site will use a SQLITE database in the root directory.
# Simply run: python manage.py syncdb
# To begin using the site.
# If you'd like to use a mysql database instead, uncomment the following lines and
# set the username, password, and name of database
# 
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql', 	# Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlit$
#         'NAME': 'infxbooklist',              	# Or path to database file if using sqlite3.
#         'USER': 'booklist_admin',               # Not used with sqlite3.
#         'PASSWORD': 'aiL9thah',					# Not used with sqlite3.
#         'HOST': '',             				# Set to empty string for localhost. Not used with sqlite3.
#         'PORT': '',                  			# Set to empty string for default. Not used with sqlite3.
#     }
# }

# UCINetIDs of those individuals you would like to administer the site
ADMIN_UCINETIDS = (
	'kaufmans', 
	'kay', 
	'royr', 
	'sparksc', 
	'pchsu', 
	'jfulmer', 
	'janoc'
)

# SSL encrypted pages
SSL_URLS = (
	r'/login/',
	r'/edit/',
	r'/add/',
	r'/update/',
	r'/delete/',
	r'/updateprofile/'
	r'/admin/',
)
