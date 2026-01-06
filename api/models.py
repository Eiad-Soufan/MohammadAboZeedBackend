# api/models.py
from django.conf import settings
from django.db import models
from django.utils.text import slugify

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# ========= أدوات مشتركة =========

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True


# ========= المستخدمون =========
# ==============================
class UserProfile(TimeStampedModel):
    """
    بروفايل إضافي لكل مستخدم مسجّل.
    المحتوى يُدار من صاحب الموقع فقط (وليس من المستخدمين).
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    display_name = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True)        # صورة خارجية (Cloudinary/AWS)
    phone = models.CharField(max_length=40, blank=True)
    website = models.URLField(blank=True)
    socials = models.JSONField(default=dict, blank=True)  # {"linkedin": "...", "x": "..."}
    def __str__(self):
        return self.display_name or self.user.get_username()


# ========= المقالات (يديرها صاحب الموقع فقط) =========
# ==============================
class Article(TimeStampedModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=230, unique=True, blank=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField()                        # Markdown/HTML
    cover_url = models.URLField(blank=True)             # صورة خارجية
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    url = models.URLField(blank=True)   
    # بديل خفيف عن الوسوم:
    keywords = models.JSONField(default=list, blank=True)   # ["ذكاء اصطناعي","Python",...]

    class Meta:
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_published", "published_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# ========= قاعدة مشتركة للكورسات =========
# ==============================
class _CourseBase(TimeStampedModel):
    """
    أساس مشترك لجدولي الكورسات:
    - CourseRecorded  (مسجّلة/فيديو)
    - CourseOnsite    (حضورية/وجاهية)
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=230, unique=True, blank=True)
    summary = models.TextField(blank=True)                 # وصف مختصر لبطاقة العرض
    long_description = models.TextField()                  # توصيف طويل
    image_url = models.URLField(blank=True)                # صورة خارجية

    # تعدادات نقطية
    objectives = models.JSONField(default=list, blank=True)       # ["هدف 1", "هدف 2", ...]
    target_audience = models.JSONField(default=list, blank=True)  # ["طلاب", "محترفون", ...]

    # محاور متعددة المستويات:
    # [{"title":"المحور الأول","bullets":["نقطة","نقطة"]}, ...]
    outline = models.JSONField(default=list, blank=True)
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    request_enabled = models.BooleanField(default=True)
    # بديل خفيف عن الوسوم:
    keywords = models.JSONField(default=list, blank=True)
    url = models.URLField(blank=True)   
    class Meta:
        abstract = True
        indexes = [models.Index(fields=["slug"]), models.Index(fields=["is_published"])]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class CourseRecorded(_CourseBase):
    """كورسات مُسجّلة (فيديو/أونلاين ذاتي)."""
    pass


class CourseOnsite(_CourseBase):
    """كورسات حضورية/وجاهية (in-person)."""
    # أمثلة مستقبلية:
    # location = models.CharField(max_length=160, blank=True)
    # seats = models.PositiveIntegerField(null=True, blank=True)
    pass


# ========= الكتب =========
# ==============================
class Book(TimeStampedModel):
    title = models.CharField(max_length=200)
    author_name = models.CharField(max_length=160, blank=True)
    description = models.TextField(blank=True)
    cover_url = models.URLField(blank=True)              # صورة خارجية
    url = models.URLField(blank=True)                # رابط شراء/تحميل
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    request_enabled = models.BooleanField(default=True)
    # بديل خفيف عن الوسوم:
    keywords = models.JSONField(default=list, blank=True)

    class Meta:
        indexes = [models.Index(fields=["title"]), models.Index(fields=["is_published"])]

    def __str__(self):
        return self.title

# ========= الأدوات =========

class Tool(TimeStampedModel):
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)              # صورة خارجية
    url = models.URLField(blank=True)               # رابط الأداة/الموقع
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    request_enabled = models.BooleanField(default=True)
    # بديل خفيف عن الوسوم:
    keywords = models.JSONField(default=list, blank=True)

    class Meta:
        indexes = [models.Index(fields=["name"]), models.Index(fields=["is_published"]), models.Index(fields=["is_featured"])]

    def __str__(self):
        return self.name
