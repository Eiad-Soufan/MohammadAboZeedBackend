# api/serializers.py
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    UserProfile,
    CourseRecorded,
    CourseOnsite,
    Book,
    Tool,
)

User = get_user_model()

# ---------------------------
# Helpers (متاحة للاستيراد من views)
# ---------------------------

def get_or_create_profile(user: User):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile

def serialize_me(user: User):
    profile = None
    try:
        profile = get_or_create_profile(user)
    except Exception:
        pass

    full_name = ""
    if hasattr(user, "full_name") and user.full_name:
        full_name = user.full_name
    else:
        full_name = f"{getattr(user,'first_name','')} {getattr(user,'last_name','')}".strip()

    data = {
        "id": user.id,
        "username": getattr(user, "username", "") or "",
        "email": getattr(user, "email", "") or "",
        "full_name": full_name,
        "profile": {
            "display_name": "",
            "bio": "",
            "avatar_url": "",
            "phone": "",
            "website": "",
            "socials": {},
        },
    }
    if profile:
        data["profile"].update({
            "display_name": getattr(profile, "display_name", "") or "",
            "bio": getattr(profile, "bio", "") or "",
            "avatar_url": getattr(profile, "avatar_url", "") or "",
            "phone": getattr(profile, "phone", "") or "",
            "website": getattr(profile, "website", "") or "",
            "socials": getattr(profile, "socials", {}) or {},
        })
    return data

def issue_tokens_for_user(user: User):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}

# ---------------------------
# 1) تسجيل الدخول: يسمح بالبريد أو اسم المستخدم ويعيد me مع التوكنات
# ---------------------------

class EmailOrUsernameTokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        identifier = attrs.get("email") or attrs.get(self.username_field) or attrs.get("username")
        password = attrs.get("password")
        if not identifier or not password:
            raise serializers.ValidationError("Email/Username and password are required.")

        try:
            user = User.objects.get(Q(email__iexact=identifier) | Q(username__iexact=identifier))
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials.")

        # مرّر username_field المتوقّع لـ SimpleJWT
        attrs[self.username_field] = getattr(user, self.username_field, user.username)
        data = super().validate(attrs)
        data["me"] = serialize_me(user)
        return data

# ---------------------------
# 2) التسجيل/فتح حساب
# ---------------------------

class RegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)
    phone = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def create(self, validated_data):
        full_name = validated_data.get("full_name", "").strip()
        email = validated_data["email"].strip().lower()
        password = validated_data["password"]
        phone = validated_data.get("phone", "").strip()

        base_username = email.split("@")[0]
        username = base_username
        i = 1
        while User.objects.filter(username__iexact=username).exists():
            i += 1
            username = f"{base_username}{i}"

        with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, password=password)
            if hasattr(user, "full_name"):
                user.full_name = full_name
                user.save(update_fields=["full_name"])
            profile = get_or_create_profile(user)
            if not getattr(profile, "display_name", ""):
                profile.display_name = full_name or username
            if phone:
                profile.phone = phone
            profile.save()
        return user

# ---------------------------
# 3) تحديث /api/me/
# ---------------------------

class MeUpdateSerializer(serializers.Serializer):
    display_name = serializers.CharField(required=False, allow_blank=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    avatar_url = serializers.URLField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    website = serializers.URLField(required=False, allow_blank=True)
    socials = serializers.JSONField(required=False)
    full_name = serializers.CharField(required=False, allow_blank=True)

    def update(self, instance: User, validated_data):
        profile = get_or_create_profile(instance)

        if "full_name" in validated_data and hasattr(instance, "full_name"):
            instance.full_name = validated_data["full_name"]
            instance.save(update_fields=["full_name"])

        for f in ["display_name", "bio", "avatar_url", "phone", "website"]:
            if f in validated_data:
                setattr(profile, f, validated_data[f])

        if "socials" in validated_data:
            val = validated_data["socials"] or {}
            if not isinstance(val, dict):
                raise serializers.ValidationError({"socials": "Must be an object/dict."})
            profile.socials = val

        profile.save()
        return instance


# ======== Recorded Courses ========

class CourseRecordedListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseRecorded
        fields = [
            "id",
            "title",
            "slug",
            "summary",
            "image_url",
            "is_featured",
            "is_published",
            "request_enabled",
            "keywords",
            "created_at",
        ]
        read_only_fields = fields  # للعرض فقط في قوائم

class CourseRecordedDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseRecorded
        fields = [
            "id",
            "title",
            "slug",
            "summary",
            "long_description",
            "image_url",
            "objectives",
            "target_audience",
            "outline",
            "is_featured",
            "is_published",
            "request_enabled",
            "keywords",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields  # API للقراءة فقط حالياً


# ======== Onsite Courses ========

class CourseOnsiteListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseOnsite
        fields = [
            "id",
            "title",
            "slug",
            "summary",
            "image_url",
            "is_featured",
            "is_published",
            "request_enabled",
            "keywords",
            "created_at",
        ]
        read_only_fields = fields

class CourseOnsiteDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseOnsite
        fields = [
            "id",
            "title",
            "slug",
            "summary",
            "long_description",
            "image_url",
            "objectives",
            "target_audience",
            "outline",
            "is_featured",
            "is_published",
            "request_enabled",
            "keywords",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


# ======== Books (قوائم + تفاصيل) ========

class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author_name",
            "description",          # مختصر للبطاقة؛ إن رغبتَ لاحقًا يمكن الاقتصار على مقتطف
            "cover_url",
            "buy_url",
            "is_featured",
            "is_published",
            "request_enabled",
            "keywords",
            "created_at",
        ]
        read_only_fields = fields

class BookDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author_name",
            "description",
            "cover_url",
            "buy_url",
            "is_featured",
            "is_published",
            "request_enabled",
            "keywords",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


# ======== Tools (قوائم + تفاصيل) ========

class ToolListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = [
            "id",
            "name",
            "description",
            "image_url",
            "link_url",
            "is_featured",
            "is_published",
            "request_enabled",
            "keywords",
            "created_at",
        ]
        read_only_fields = fields

class ToolDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = [
            "id",
            "name",
            "description",
            "image_url",
            "link_url",
            "is_featured",
            "is_published",
            "request_enabled",
            "keywords",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


# ===== Articles =====
from rest_framework import serializers
from .models import Article

class ArticleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = (
            "id",
            "slug",
            "title",
            "excerpt",
            "cover_url",
            "published_at",
            "keywords",
        )

class ArticleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = (
            "id",
            "slug",
            "title",
            "excerpt",
            "content",
            "cover_url",
            "is_published",
            "published_at",
            "keywords",
        )
