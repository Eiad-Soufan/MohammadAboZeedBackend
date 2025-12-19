# api/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django import forms

from django_svelte_jsoneditor.widgets import SvelteJSONEditorWidget

from .models import (
    UserProfile, Article, Book, Tool,
    CourseRecorded, CourseOnsite,
)

# ============================
# عنوان لوحة الإدارة
# ============================
admin.site.site_header = "لوحة إدارة المدونة"
admin.site.site_title  = "إدارة المحتوى"
admin.site.index_title = "مرحبًا بك 👋 — اختر ما تريد إدارته"

# ============================
# JSON Schemas (اختياري)
# ============================
OBJECTIVES_SCHEMA = {
    "type": "array",
    "title": "الأهداف",
    "items": {"type": "string", "title": "هدف"},
}

AUDIENCE_SCHEMA = {
    "type": "array",
    "title": "الفئة المستهدفة",
    "items": {"type": "string", "title": "فئة"},
}

OUTLINE_SCHEMA = {
    "type": "array",
    "title": "المحتوى التفصيلي (Outline)",
    "items": {
        "type": "object",
        "title": "قسم",
        "properties": {
            "title":   {"type": "string", "title": "عنوان القسم"},
            "bullets": {
                "type": "array",
                "title": "نقاط القسم",
                "items": {"type": "string", "title": "نقطة"}
            }
        },
        "required": ["title"],
        "additionalProperties": False
    }
}

# ============================
# ويدجت JSON
# ============================
def json_widget(schema=None, height="380px"):
    try:
        return SvelteJSONEditorWidget(schema=schema, attrs={"style": f"min-height:{height};"})
    except TypeError:
        return SvelteJSONEditorWidget(attrs={"style": f"min-height:{height};"})

# ============================
# محوّلات النص ↔ JSON
# ============================
def _to_list(text: str):
    """من نص متعدد الأسطر إلى list[str] (يتجاهل الفارغ)."""
    lines = [ln.strip() for ln in (text or "").splitlines()]
    return [ln for ln in lines if ln]

def _list_to_text(items):
    """من list[str] إلى نص متعدد الأسطر."""
    if not items:
        return ""
    return "\n".join(str(x).strip() for x in items if str(x).strip())

def _parse_outline(text: str):
    """
    يدعم:
    1) Markdown:
       # عنوان
       - نقطة 1
       - نقطة 2

       # قسم آخر
       - ...

    2) سطر واحد:
       عنوان: نقطة1؛ نقطة2 | الفواصل ; ؛ | ,
    """
    import re
    text = (text or "").strip()
    if not text:
        return []

    sections = []
    current = None
    has_md_titles = any(ln.strip().startswith("#") for ln in text.splitlines())

    if has_md_titles:
        for raw in text.splitlines():
            ln = raw.strip()
            if not ln:
                continue
            if ln.startswith("#"):
                title = ln.lstrip("#").strip()
                if title:
                    current = {"title": title, "bullets": []}
                    sections.append(current)
                continue
            if re.match(r"^[-*\u2022]\s+", ln):
                bullet = re.sub(r"^[-*\u2022]\s+", "", ln).strip()
                if bullet and current:
                    current["bullets"].append(bullet)
        return [s for s in sections if s.get("title")]

    for raw in text.splitlines():
        ln = raw.strip()
        if not ln:
            continue
        if ":" in ln:
            title, rest = ln.split(":", 1)
            title = title.strip()
            bullets = re.split(r"[;؛\|,]", rest)
            bullets = [b.strip() for b in bullets if b.strip()]
            sections.append({"title": title, "bullets": bullets})
        else:
            sections.append({"title": ln, "bullets": []})
    return sections

def _outline_to_text(sections):
    """
    من outline كـ list[{"title":..., "bullets":[...]}] إلى نص ماركداون.
    """
    if not sections:
        return ""
    lines = []
    for sec in sections:
        title = str(sec.get("title", "")).strip()
        if not title:
            continue
        lines.append(f"# {title}")
        for b in (sec.get("bullets") or []):
            b = str(b).strip()
            if b:
                lines.append(f"- {b}")
        lines.append("")  # سطر فارغ بين الأقسام
    # إزالة آخر سطر فارغ إن وجد
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)

# ============================
# Forms للكورسات: إدخال نصي + محرر JSON
# ============================
class CourseRecordedForm(forms.ModelForm):
    # حقول نصية مساعدة (لا تُخزَّن في DB)
    objectives_text = forms.CharField(
        label="أهداف (نص بسيط)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "اكتب كل هدف في سطر مستقل"})
    )
    target_audience_text = forms.CharField(
        label="الفئة المستهدفة (نص بسيط)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "اكتب كل فئة في سطر مستقل"})
    )
    outline_text = forms.CharField(
        label="Outline (نص بسيط)",
        required=False,
        help_text=(
            "صيغة ماركداون:\n"
            "# عنوان القسم\n- نقطة 1\n- نقطة 2\n\n"
            "# قسم آخر\n- ...\n\n"
            "أو صيغة سطر واحد: عنوان: نقطة1؛ نقطة2"
        ),
        widget=forms.Textarea(attrs={"rows": 8})
    )

    class Meta:
        model  = CourseRecorded
        fields = "__all__"
        widgets = {
            "objectives":      json_widget(schema=OBJECTIVES_SCHEMA, height="260px"),
            "target_audience": json_widget(schema=AUDIENCE_SCHEMA,  height="260px"),
            "outline":         json_widget(schema=OUTLINE_SCHEMA,   height="360px"),
        }

    def __init__(self, *args, **kwargs):
        """
        تعبئة الحقول النصّية بقيمة الـ JSON الحالية للعرض المسبق.
        (لا نكتب على JSON إلا إذا المستخدم حرّر النص بالفعل)
        """
        super().__init__(*args, **kwargs)
        inst = getattr(self, "instance", None)
        if inst and inst.pk:
            # عرض الأهداف والفئة كسطور
            self.fields["objectives_text"].initial = _list_to_text(getattr(inst, "objectives", None))
            self.fields["target_audience_text"].initial = _list_to_text(getattr(inst, "target_audience", None))
            # عرض الـ outline كنص ماركداون
            self.fields["outline_text"].initial = _outline_to_text(getattr(inst, "outline", None))

    def clean(self):
        cleaned = super().clean()
        # إذا المستخدم كتب نصًا، حوّل واكتب على JSON
        if cleaned.get("objectives_text"):
            cleaned["objectives"] = _to_list(cleaned["objectives_text"])
        if cleaned.get("target_audience_text"):
            cleaned["target_audience"] = _to_list(cleaned["target_audience_text"])
        if cleaned.get("outline_text"):
            cleaned["outline"] = _parse_outline(cleaned["outline_text"])
        return cleaned

class CourseOnsiteForm(forms.ModelForm):
    objectives_text = forms.CharField(
        label="أهداف (نص بسيط)", required=False,
        widget=forms.Textarea(attrs={"rows": 4})
    )
    target_audience_text = forms.CharField(
        label="الفئة المستهدفة (نص بسيط)", required=False,
        widget=forms.Textarea(attrs={"rows": 4})
    )
    outline_text = forms.CharField(
        label="Outline (نص بسيط)", required=False,
        help_text="صيغة ماركداون أو: عنوان: نقطة1؛ نقطة2",
        widget=forms.Textarea(attrs={"rows": 8})
    )

    class Meta:
        model  = CourseOnsite
        fields = "__all__"
        widgets = {
            "objectives":      json_widget(schema=OBJECTIVES_SCHEMA, height="260px"),
            "target_audience": json_widget(schema=AUDIENCE_SCHEMA,  height="260px"),
            "outline":         json_widget(schema=OUTLINE_SCHEMA,   height="360px"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        inst = getattr(self, "instance", None)
        if inst and inst.pk:
            self.fields["objectives_text"].initial = _list_to_text(getattr(inst, "objectives", None))
            self.fields["target_audience_text"].initial = _list_to_text(getattr(inst, "target_audience", None))
            self.fields["outline_text"].initial = _outline_to_text(getattr(inst, "outline", None))

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("objectives_text"):
            cleaned["objectives"] = _to_list(cleaned["objectives_text"])
        if cleaned.get("target_audience_text"):
            cleaned["target_audience"] = _to_list(cleaned["target_audience_text"])
        if cleaned.get("outline_text"):
            cleaned["outline"] = _parse_outline(cleaned["outline_text"])
        return cleaned

# ============================
# User/Profile
# ============================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "phone", "website", "updated_at")
    search_fields = ("user__username", "user__email", "display_name", "phone")
    list_select_related = ("user",)

# ============================
# Articles
# ============================
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "published_at", "created_at")
    list_filter  = ("is_published",)
    search_fields = ("title", "excerpt", "content", "keywords")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    readonly_fields = ("created_at", "updated_at")

# ============================
# Courses
# ============================
@admin.register(CourseRecorded)
class CourseRecordedAdmin(admin.ModelAdmin):
    form = CourseRecordedForm
    list_display = ("title", "is_published", "is_featured", "created_at")
    list_filter  = ("is_published", "is_featured")
    search_fields = ("title", "summary", "long_description", "keywords")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("المعلومات الأساسية", {
            "fields": ("title", "slug", "is_published", "is_featured", "keywords", "summary", "long_description")
        }),
        ("إدخال سريع بالنص (يُحوَّل تلقائياً إلى JSON)", {
            "fields": ("objectives_text", "target_audience_text", "outline_text"),
            "description": "اكتب نصًا بسيطًا؛ سنحوّله تلقائيًا ونملأ به حقول JSON أدناه."
        }),
        ("حقول JSON (يمكن تعديلها يدويًا عند الحاجة)", {
            "fields": ("objectives", "target_audience", "outline"),
            "classes": ("collapse",)
        }),
        ("نظام", {"fields": ("created_at", "updated_at")}),
    )

@admin.register(CourseOnsite)
class CourseOnsiteAdmin(admin.ModelAdmin):
    form = CourseOnsiteForm
    list_display = ("title", "is_published", "is_featured", "created_at")
    list_filter  = ("is_published", "is_featured")
    search_fields = ("title", "summary", "long_description", "keywords")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("المعلومات الأساسية", {
            "fields": ("title", "slug", "is_published", "is_featured", "keywords", "summary", "long_description")
        }),
        ("إدخال سريع بالنص (يُحوَّل تلقائياً إلى JSON)", {
            "fields": ("objectives_text", "target_audience_text", "outline_text"),
        }),
        ("حقول JSON (يمكن تعديلها يدويًا عند الحاجة)", {
            "fields": ("objectives", "target_audience", "outline"),
            "classes": ("collapse",)
        }),
        ("نظام", {"fields": ("created_at", "updated_at")}),
    )

# ============================
# Books & Tools
# ============================
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author_name", "is_published", "is_featured", "created_at")
    list_filter  = ("is_published", "is_featured")
    search_fields = ("title", "author_name", "description", "keywords")
    readonly_fields = ("created_at", "updated_at")

@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ("name", "is_published", "is_featured", "created_at", "link_preview")
    list_filter  = ("is_published", "is_featured")
    search_fields = ("name", "description", "keywords")
    readonly_fields = ("created_at", "updated_at")

    def link_preview(self, obj):
        link = getattr(obj, "link_url", None)
        if link:
            return format_html('<a href="{}" target="_blank">فتح الرابط</a>', link)
        return "-"
    link_preview.short_description = "رابط الأداة"
