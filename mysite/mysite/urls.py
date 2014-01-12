from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',

	url(r'^$', 'weixin.views.home', name='home'),\

	url(r'^weixin$', 'weixin.views.weixin', name='weixin'),
	url(r'^weixin2$', 'weixin.view2.handleRequest', name='weixin2'),
    # Examples:
    # url(r'^$', 'weixin.views.home', name='home'),
    # url(r'^weixin/', include('weixin.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
