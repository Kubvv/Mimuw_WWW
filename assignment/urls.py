"""assignment URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from serverSide import views
from serverSide.views import index, directoryCreate, fileCreate, deletionView, directoryDelete, saveProver, saveVc, compile, logout, preindex, showFileJS, compileJS, deleteDirJS, deleteFileJS, changeThemeJS

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', index, name='index'),
    path('dir_create/', directoryCreate, name='dir_create'),
    path('file_create/', fileCreate, name='file_create'),
    path('delete/', deletionView, name='delete'),
    path('directory_delete/<int:pk>/', views.directoryDelete, name='directoryDelete'),
    path('file_delete/<int:pk>/', views.fileDelete, name='fileDelete'),
    path('show_file/<int:pk>/', views.showFile, name='showFile'),
    path('show_tab/<str:tab>/', views.showTab, name='showTab'),
    path('show_tab/prover/select_prover/', views.saveProver, name='saveProv'),
    path('show_tab/vcs/select_vc/', views.saveVc, name='saveVc'),
    path('compile/', views.compile, name='compile'),
    path('logoutuser/', views.logout, name='logout'),
    path('pre-index/', views.preindex, name='preindex'),
    path('', include("django.contrib.auth.urls"))
]

urlpatterns += [
    url(r'^ajax/show_file/$', views.showFileJS, name='show_file_js'),
    url(r'^ajax/compile/$', views.compileJS, name="compile_js"),
    url(r'^ajax/delete/$', views.deleteJS, name="delete_js"),
    url(r'^ajax/delete_file/$', views.deleteFileJS, name="delete_file_js"),
    url(r'^ajax/delete_dir/$', views.deleteDirJS, name="delete_dir_js"),
    url(r'^ajax/change_theme/$', views.changeThemeJS, name="change_theme_js")
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
