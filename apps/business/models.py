from django.db import models


def default_ai_restrictions():
    return [
        "Never invent business information.",
        "Never invent a customer's experience.",
        "Never change the customer's sentiment.",
        "Never make unsupported claims.",
        "Never pretend something happened when it was not provided by the customer."
    ]


class BusinessProfile(models.Model):
    # 1. Business Information
    name = models.CharField(max_length=255, verbose_name="Business Name")
    category = models.CharField(max_length=100, verbose_name="Business Category")
    category_other = models.CharField(max_length=100, blank=True, null=True, verbose_name="Other Category")
    location = models.CharField(max_length=255, verbose_name="Business Location")
    description = models.TextField(verbose_name="Business Description", help_text="What does your business do? Describe it in 1-2 sentences.")

    # 2. Products / Services
    products_services = models.JSONField(default=list, verbose_name="Products or Services Offered")
    main_specialty_products = models.JSONField(default=list, verbose_name="Main / Specialty Products or Services")

    # 3. Brand Personality
    brand_tone = models.JSONField(default=list, verbose_name="Brand Tone/Sound")
    communication_length = models.CharField(max_length=50, verbose_name="Communication Length")
    communication_style = models.CharField(max_length=50, verbose_name="Writing Style")
    preferred_languages = models.JSONField(default=list, verbose_name="Preferred Languages")
    preferred_language_other = models.CharField(max_length=100, blank=True, null=True, verbose_name="Other Language")

    # 4. Business Knowledge
    differentiator = models.TextField(verbose_name="What Makes Business Different", help_text="What are you known for? What makes you different from other businesses?")
    important_facts = models.TextField(verbose_name="Important Business Facts", help_text="What important factual information should the AI know about your business?")

    # 5. AI Restrictions
    default_ai_rules = models.JSONField(default=default_ai_restrictions, verbose_name="Default AI Restrictions")
    custom_restrictions = models.TextField(blank=True, null=True, verbose_name="Additional Restrictions", help_text="Anything the AI should never claim, assume, mention, or promise?")

    # 6. Google Review
    google_review_url = models.URLField(max_length=500, verbose_name="Google Review URL")

    # Optional Information
    website = models.URLField(max_length=500, blank=True, null=True, verbose_name="Website URL")
    opening_hours = models.TextField(blank=True, null=True, verbose_name="Opening Hours")
    target_customers = models.JSONField(default=list, blank=True, verbose_name="Target Customers")
    faqs = models.JSONField(default=list, blank=True, verbose_name="Frequently Asked Questions")
    business_story = models.TextField(blank=True, null=True, verbose_name="Business Story")
    important_terminology = models.TextField(blank=True, null=True, verbose_name="Important Terminology")

    # Configuration & Analytics
    is_configured = models.BooleanField(default=False, verbose_name="Configuration Completed")
    total_views = models.PositiveIntegerField(default=0, verbose_name="Total Customer Views")
    total_ai_generated = models.PositiveIntegerField(default=0, verbose_name="Total AI Reviews Generated")
    total_copies_redirects = models.PositiveIntegerField(default=0, verbose_name="Total Copies & Redirects")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or "Business Profile"


class AIConfig(models.Model):
    PROVIDER_CHOICES = [
        ('openai', 'OpenAI (GPT-4o / GPT-4o-mini)'),
        ('gemini', 'Google Gemini (Gemini 1.5 Flash / Pro)'),
        ('groq', 'Groq (Llama 3.1 / Mixtral)'),
        ('anthropic', 'Anthropic (Claude 3.5 Haiku / Sonnet)'),
    ]

    business = models.OneToOneField(BusinessProfile, on_delete=models.CASCADE, related_name='ai_config')
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES, default='openai', verbose_name="AI Provider")
    api_key = models.CharField(max_length=500, verbose_name="API Key")
    model_name = models.CharField(max_length=100, default='gpt-4o-mini', verbose_name="Model Designation")
    is_active = models.BooleanField(default=False, verbose_name="Key Verified & Active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.business.name} - {self.provider} ({self.model_name})"
