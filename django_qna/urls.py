"""django_qna URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import reverse
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
]
urlpatterns += [
    path("", include("qna.urls")),
]
# Add URL maps to redirect the base URL to our application
# urlpatterns += [
#     path('', RedirectView.as_view(url='qna/', permanent=True)),
# ]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

settings.LOGIN_URL = reverse("qna-login")
settings.LOGIN_REDIRECT_URL = reverse("qna-home")
settings.LOGOUT_REDIRECT_URL = reverse("qna-home")

handler404 = "qna.views.response_404_error_handler"
handler500 = "qna.views.response_500_error_handler"
handler403 = "qna.views.response_403_error_handler"
handler400 = "qna.views.response_400_error_handler"
CSRF_FAILURE_VIEW = "qna.views.csrf_failure"
