from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('home/', include('landing.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('blog.urls'))
]
