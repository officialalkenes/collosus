from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("superaccess/", admin.site.urls),
    # path('', include('investment.urls', namespace='investment')),
    path("accounts/", include("users.urls", namespace="accounts")),
    path("accounts/", include("django.contrib.auth.urls")),
    # path('profiles/', include('profiles.urls', namespace='profiles')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Crypto Colossus Admin"
admin.site.index_title = "Welcome To Crypto Colossus Admin Portal"
admin.site.site_title = "Crypto Colossus Admin Portal"

# handler404 = 'users.views.handler404'
# handler500 = 'users.views.handle_server_error'
