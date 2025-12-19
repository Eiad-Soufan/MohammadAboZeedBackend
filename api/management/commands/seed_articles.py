# api/management/commands/seed_articles.py
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from api.models import Article

ARTICLES = [
    {
        "title": "ما الذي يميّز القيادة الاستراتيجية المعاصرة؟",
        "excerpt": "مبادئ عملية لبناء رؤية قابلة للتنفيذ، وقياس الأثر في مؤسسات سريعة التغيّر.",
        "cover_url": "https://images.unsplash.com/photo-1581090464777-f3220bbe1b8b?q=80&w=1200&auto=format&fit=crop",
        "keywords": ["قيادة", "استراتيجية", "تحول"],
        "content": """
<h2>لماذا القيادة الاستراتيجية الآن؟</h2>
<p>تسارع التغيّر يحتم علينا الانتقال من التخطيط السنوي إلى <strong>التكيّف المستمر</strong>.</p>
<ul>
  <li>ترسيخ الأولويات ووضوح التوجّه.</li>
  <li>مؤشرات أداء تقود القرار لا تزيّنه.</li>
  <li>حلقات تعلم قصيرة وتكرار محسوب.</li>
</ul>
<hr/>
<p><em>خلاصة:</em> الاستراتيجية ليست وثيقة، بل نظام حوكمة وتعّلم.</p>
""",
    },
    {
        "title": "خارطة طريق لتحسين العمليات بدون بيروقراطية",
        "excerpt": "نموذج عملي لتبسيط الإجراءات مع الحفاظ على الجودة والامتثال.",
        "cover_url": "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?q=80&w=1200&auto=format&fit=crop",
        "keywords": ["عمليات", "تحسين", "جودة"],
        "content": """
<h2>ابدأ بالملاحظات قبل القياس</h2>
<p>استمع للفرق الأمامية؛ فهي ترى الاختناقات مبكرًا.</p>
<ol>
  <li>خريطة تدفق بسيطة للمنهج الحالي.</li>
  <li>تحديد نقاط التعطّل والأدوار.</li>
  <li>تجربة تحسين محدودة الأثر ثم التوسّع.</li>
</ol>
<p>اعتمد قاعدة: <strong>وثّق أقل، اختبر أكثر</strong>.</p>
""",
    },
    {
        "title": "بناء ثقافة التعلّم في المؤسسات الحكومية",
        "excerpt": "كيف ننتقل من الدورات الموسمية إلى التعلم كعادة تشغيلية يومية.",
        "cover_url": "https://images.unsplash.com/photo-1551836022-d5d88e9218df?q=80&w=1200&auto=format&fit=crop",
        "keywords": ["تعلم", "موارد بشرية", "حكومة"],
        "content": """
<h2>من التعلم كنشاط إلى التعلم كنظام</h2>
<p>ادمج التعلم في تدفق العمل عبر مراجعات قصيرة بعد المشاريع.</p>
<ul>
  <li>جلسات <code>After Action Review</code>.</li>
  <li>مكتبة معارف داخلية قابلة للبحث.</li>
  <li>مكافآت للسلوك التعلمي، لا للحضور فقط.</li>
</ul>
""",
    },
    {
        "title": "تحويل الرؤية إلى مبادرات قابلة للقياس",
        "excerpt": "إطار بسيط من 4 خطوات لربط الرؤية بالمؤشرات والتمويل.",
        "cover_url": "https://images.unsplash.com/photo-1529336953121-ad5a0d43d0ee?q=80&w=1200&auto=format&fit=crop",
        "keywords": ["مؤشرات", "تنفيذ", "حوكمة"],
        "content": """
<h2>سلم الترابط</h2>
<p>الرؤية ← الأهداف الإستراتيجية ← المبادرات ← مؤشرات النتائج والمخرجات.</p>
<p>تأكّد أن لكل مبادرة <strong>مالك، ميزانية، وتاريخ مراجعة</strong>.</p>
""",
    },
    {
        "title": "رحلة العميل الداخلية: خدمة الموظف أولًا",
        "excerpt": "ما لا يقاس لا يُحسَّن: اجعل تجربة الموظف أساسًا لتحسين الخدمة العامة.",
        "cover_url": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?q=80&w=1200&auto=format&fit=crop",
        "keywords": ["تجربة الموظف", "خدمة", "CX"],
        "content": """
<h2>رحلة واضحة، نقاط تماس قليلة</h2>
<p>قلّل عدد الأنظمة التي يمرّ بها الموظف واحذف الخطوات غير الضرورية.</p>
<ul>
  <li>بوابة موحّدة للطلبات.</li>
  <li>سياسات مكتوبة بنبرة إنسانية.</li>
  <li>تقارير زمنية لحلّ الطلبات.</li>
</ul>
""",
    },
    {
        "title": "من مؤشرات النشاط إلى مؤشرات الأثر",
        "excerpt": "غيّر السؤال: ماذا فعلنا؟ إلى ماذا تغيّر؟",
        "cover_url": "https://images.unsplash.com/photo-1496307042754-b4aa456c4a2d?q=80&w=1200&auto=format&fit=crop",
        "keywords": ["KPI", "أثر", "قياس"],
        "content": """
<h2>ثلاث طبقات للمؤشرات</h2>
<p>نشاط &rarr; مخرجات &rarr; نتائج/أثر. ابدأ من الأثر وارجع للخلف.</p>
<p><strong>قاعدة:</strong> مؤشرك الجيد يقود قرارًا فعليًا أو يوقف مبادرة.</p>
""",
    },
    {
        "title": "التواصل القيادي: وضوح، قِصَر، وتكرار",
        "excerpt": "رسالة قيادية فعّالة تُبنى على ثلاثة مبادئ بسيطة.",
        "cover_url": "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?q=80&w=1200&auto=format&fit=crop",
        "keywords": ["تواصل", "قيادة", "ثقافة"],
        "content": """
<h2>قانون 3×3</h2>
<p>ثلاث رسائل محورية × تُكرّر ثلاث مرّات × عبر ثلاث قنوات.</p>
<p>اسأل نفسك: ما جملة واحدة لو تذكّرها الجميع هذا الأسبوع سننجح؟</p>
""",
    },
    {
        "title": "فرق رشيقة في بيئات غير تقنية",
        "excerpt": "كيف نستعير مبادئ الرشاقة دون تعقيد الأدوات.",
        "cover_url": "https://images.unsplash.com/photo-1552664730-d307ca884978?q=80&w=1200&auto=format&fit=crop",
        "keywords": ["Agile", "فرق", "إدارة مشاريع"],
        "content": """
<h2>رشاقة بلا تعقيد</h2>
<p>لوحة عمل أسبوعية، اجتماع وقوف 10 دقائق، ونسخة منتج صغرى كل ربع سنة.</p>
<ul>
  <li>تقليل العمل الجاري WIP.</li>
  <li>تعليقات أصحاب المصلحة مبكرًا.</li>
  <li>تحسين مستمر Retrospective.</li>
</ul>
""",
    },
    {
        "title": "حوكمة مبسّطة للابتكار",
        "excerpt": "دع الابتكار يعيش داخل حدود واضحة ومساحة آمنة للتجربة.",
        "cover_url": "https://images.unsplash.com/photo-1518779578993-ec3579fee39f?q=80&w=1200&auto=format&fit=crop",
        "keywords": ["ابتكار", "حوكمة", "منتجات"],
        "content": """
<h2>إطار 70/20/10</h2>
<p>70% تشغيل أساسي، 20% تحسين تدريجي، 10% تجارب عالية المخاطرة.</p>
<p>خصّص ميزانية صغيرة للتجربة، لكن بمقاييس نجاح واضحة وزمن إيقاف.</p>
""",
    },
    {
        "title": "تصميم خدمات عامة تتمحور حول الإنسان",
        "excerpt": "مبادئ ومهارات لجعل رحلة المستفيد سلسة وشخصية.",
        "cover_url": "https://images.unsplash.com/photo-1487014679447-9f8336841d58?q=80&w=1200&auto=format&fit=crop",
        "keywords": ["تصميم خدمات", "مستخدم", "تجربة"],
        "content": """
<h2>ابدأ بالاحتياج الحقيقي</h2>
<p>مقابلات قصيرة، نماذج أولية سريعة، واختبارات استخدام شبه أسبوعية.</p>
<p>صمّم اللغة والواجهات والقرارات من منظور المستفيد أولًا.</p>
""",
    },
]

class Command(BaseCommand):
    help = "Seed 10 demo articles with working cover images and realistic Arabic content. Safe to run multiple times."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing Article records before seeding."
        )

    @transaction.atomic
    def handle(self, *args, **options):
        reset = options.get("reset")
        if reset:
            self.stdout.write(self.style.WARNING("Deleting existing Article records..."))
            Article.objects.all().delete()

        created, updated = 0, 0
        now = timezone.now()

        for i, a in enumerate(ARTICLES):
            # تواريخ متدرجة: اليوم، -2 يوم، -4 يوم... لتبدو واقعية
            published_at = now - timedelta(days=i * 2)

            obj, is_created = Article.objects.update_or_create(
                title=a["title"],
                defaults={
                    "excerpt": a.get("excerpt", ""),
                    "content": a.get("content", ""),
                    "cover_url": a.get("cover_url", ""),
                    "is_published": True,
                    "published_at": published_at,
                    "keywords": a.get("keywords", []),
                },
            )
            created += 1 if is_created else 0
            updated += 0 if is_created else 1

        self.stdout.write(
            self.style.SUCCESS(f"Articles -> created: {created}, updated: {updated}")
        )
