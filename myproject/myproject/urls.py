"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path,include
from myproject import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('jet/', include('jet.urls', 'jet')),  # Django JET
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')), 
    path('admin/', admin.site.urls),
    path('',views.index,name="index"),
    path('shop/',views.shop,name="shop"),
    path('bestseller/',views.bestseller,name="bestseller"),
    path('cart/', views.cart_page, name="cart_page"),
    path('cheackout/',views.cheackout,name="cheackout"),
    path('404/',views.f404,name="f404"),
    path('contact/',views.contact,name="contact"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("register/", views.register, name="register"),
    path('myaccount/',views.myaccount,name="myaccount"),
    path('firstitems/',views.firstitems),
    path('seconditems/',views.seconditems),
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("remove/<int:cart_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("update/<int:cart_id>/<str:action>/", views.update_quantity, name="update_quantity"),
    path("order-confirm/", views.order_confirm, name="order_confirm"),
    path("download-order-pdf/", views.download_order_pdf, name="download_order_pdf"),
    path("myorder/",views.my_order)


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
