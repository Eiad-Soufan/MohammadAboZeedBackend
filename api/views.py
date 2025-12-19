# api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination

from django.db.models import Q

from .models import CourseRecorded, CourseOnsite, Book, Tool, Article

from .serializers import (
    # Auth / Profile
    EmailOrUsernameTokenSerializer,
    RegisterSerializer,
    MeUpdateSerializer,
    serialize_me,
    # Courses
    CourseRecordedListSerializer,
    CourseRecordedDetailSerializer,
    CourseOnsiteListSerializer,
    CourseOnsiteDetailSerializer,
    # Books & Tools
    BookListSerializer,
    BookDetailSerializer,
    ToolListSerializer,
    ToolDetailSerializer,
    ArticleListSerializer,
    ArticleDetailSerializer,
)


# =========================
# Pagination موحّد
# =========================
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12                      # الافتراضي
    page_size_query_param = "page_size" # ?page_size=...
    max_page_size = 50


# =========================
# Auth
# =========================
class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = EmailOrUsernameTokenSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        return Response({"me": serialize_me(user)}, status=status.HTTP_201_CREATED)

# api/views.py

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"me": serialize_me(request.user)})

    def patch(self, request):
        ser = MeUpdateSerializer(instance=request.user, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response({"me": serialize_me(request.user)})

    # NEW: accept PUT as well (treat it like PATCH to avoid requiring all fields)
    def put(self, request):
        ser = MeUpdateSerializer(instance=request.user, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response({"me": serialize_me(request.user)})



# =========================
# Recorded Courses
# =========================
class RecordedCourseListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CourseRecordedListSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = CourseRecorded.objects.filter(is_published=True).order_by("-created_at")
        q = self.request.query_params.get("q")
        featured = self.request.query_params.get("featured")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(summary__icontains=q))
        if featured in ("1", "true", "True"):
            qs = qs.filter(is_featured=True)
        return qs

class RecordedCourseDetailView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = CourseRecordedDetailSerializer
    lookup_field = "slug"
    queryset = CourseRecorded.objects.filter(is_published=True)


# =========================
# Onsite Courses
# =========================
class OnsiteCourseListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CourseOnsiteListSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = CourseOnsite.objects.filter(is_published=True).order_by("-created_at")
        q = self.request.query_params.get("q")
        featured = self.request.query_params.get("featured")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(summary__icontains=q))
        if featured in ("1", "true", "True"):
            qs = qs.filter(is_featured=True)
        return qs

class OnsiteCourseDetailView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = CourseOnsiteDetailSerializer
    lookup_field = "slug"
    queryset = CourseOnsite.objects.filter(is_published=True)


# =========================
# Books
# =========================
class BookListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = BookListSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = Book.objects.filter(is_published=True).order_by("-created_at")
        q = self.request.query_params.get("q")
        featured = self.request.query_params.get("featured")
        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(author_name__icontains=q) |
                Q(description__icontains=q)
            )
        if featured in ("1", "true", "True"):
            qs = qs.filter(is_featured=True)
        return qs

class BookDetailView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = BookDetailSerializer
    lookup_field = "pk"
    queryset = Book.objects.filter(is_published=True)


# =========================
# Tools
# =========================
class ToolListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ToolListSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = Tool.objects.filter(is_published=True).order_by("-created_at")
        q = self.request.query_params.get("q")
        featured = self.request.query_params.get("featured")
        if q:
            qs = qs.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q)
            )
        if featured in ("1", "true", "True"):
            qs = qs.filter(is_featured=True)
        return qs

class ToolDetailView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = ToolDetailSerializer
    lookup_field = "pk"
    queryset = Tool.objects.filter(is_published=True)


# =========================
# Articles
# =========================
class ArticleListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ArticleListSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = Article.objects.all().order_by("-published_at", "-created_at")

        # نشر فقط (افتراضيًا نعم)
        published = self.request.query_params.get("published", "1")
        if published in ("1", "true", "True", "yes"):
            qs = qs.filter(is_published=True)

        # بحث
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(excerpt__icontains=q) |
                Q(content__icontains=q)
            )
        return qs


class ArticleDetailView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = ArticleDetailSerializer
    lookup_field = "slug"
    queryset = Article.objects.filter(is_published=True).order_by("-published_at", "-created_at")
