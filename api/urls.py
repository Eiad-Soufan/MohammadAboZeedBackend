from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Auth & Profile
    path("token/", LoginView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),

    # Recorded Courses
    path("courses/recorded/",              RecordedCourseListView.as_view(),   name="courses-recorded-list"),
    path("courses/recorded/<slug:slug>/",  RecordedCourseDetailView.as_view(), name="courses-recorded-detail"),

    # Onsite Courses
    path("courses/onsite/",                OnsiteCourseListView.as_view(),     name="courses-onsite-list"),
    path("courses/onsite/<slug:slug>/",    OnsiteCourseDetailView.as_view(),   name="courses-onsite-detail"),

    # Books
    path("books/",                         BookListView.as_view(),             name="books-list"),
    path("books/<int:pk>/",                BookDetailView.as_view(),           name="books-detail"),

    # Tools
    path("tools/",                         ToolListView.as_view(),             name="tools-list"),
    path("tools/<int:pk>/",                ToolDetailView.as_view(),           name="tools-detail"),
    path("articles/", ArticleListView.as_view(), name="article-list"),
    # يقبل أي نص بدون "/" — مناسب للسلاجز العربية
    path("articles/<path:slug>/", ArticleDetailView.as_view(), name="article-detail"),

]
