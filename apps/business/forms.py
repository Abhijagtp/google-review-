from django import forms
from django.contrib.auth.models import User
from .models import BusinessProfile, AIConfig


class AdminLoginForm(forms.Form):
    username = forms.CharField(
        label="Admin Username",
        widget=forms.TextInput(attrs={
            "class": "w-full px-4 py-3.5 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 placeholder-slate-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm shadow-sm transition-all",
            "placeholder": "Enter your username",
            "required": "required",
            "autocomplete": "username",
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-4 py-3.5 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 placeholder-slate-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm shadow-sm transition-all",
            "placeholder": "••••••••",
            "required": "required",
            "autocomplete": "current-password",
        })
    )


class DatabaseInstallerForm(forms.Form):
    database_url = forms.CharField(
        label="Neon PostgreSQL Database URL",
        widget=forms.TextInput(attrs={
            "class": "w-full px-4 py-3.5 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 placeholder-slate-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent font-mono text-sm shadow-sm transition-all",
            "placeholder": "postgresql://user:password@ep-xyz.region.aws.neon.tech/neondb?sslmode=require",
            "required": "required",
            "autocomplete": "off",
        }),
        help_text="Paste your Neon connection string starting with postgresql://"
    )


class AIConfigForm(forms.ModelForm):
    class Meta:
        model = AIConfig
        fields = ['provider', 'api_key', 'model_name']
        widgets = {
            'provider': forms.Select(attrs={
                'class': 'w-full px-4 py-3.5 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 focus:bg-white focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm shadow-sm transition-all',
                'id': 'id_provider',
            }),
            'api_key': forms.PasswordInput(attrs={
                'class': 'w-full px-4 py-3.5 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 placeholder-slate-400 focus:bg-white focus:ring-2 focus:ring-blue-600 focus:border-transparent font-mono text-sm shadow-sm transition-all',
                'placeholder': 'sk-... or AIzaSy...',
                'render_value': True,
            }),
            'model_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3.5 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 placeholder-slate-400 focus:bg-white focus:ring-2 focus:ring-blue-600 focus:border-transparent font-mono text-sm shadow-sm transition-all',
                'placeholder': 'gemini-2.5-flash / gpt-4o-mini',
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.api_key:
            # Render masked key preview in initial value
            self.initial['api_key'] = self.instance.masked_api_key

    def clean_api_key(self):
        key = self.cleaned_data.get('api_key', '').strip()
        if '••••' in key and self.instance and self.instance.pk:
            # Key was unchanged, retain existing encrypted key
            return self.instance.api_key
        return key



CATEGORY_CHOICES = [
    ('Restaurant', 'Restaurant'),
    ('Cafe / Coffee Shop', 'Cafe / Coffee Shop'),
    ('Bakery', 'Bakery'),
    ('Bar / Lounge', 'Bar / Lounge'),
    ('Hotel / Resort', 'Hotel / Resort'),
    ('Salon / Spa', 'Salon / Spa'),
    ('Gym / Fitness', 'Gym / Fitness'),
    ('Healthcare / Clinic', 'Healthcare / Clinic'),
    ('Dental', 'Dental'),
    ('Retail Store', 'Retail Store'),
    ('Clothing / Fashion', 'Clothing / Fashion'),
    ('Beauty / Cosmetics', 'Beauty / Cosmetics'),
    ('Electronics', 'Electronics'),
    ('Real Estate', 'Real Estate'),
    ('Automotive', 'Automotive'),
    ('Education / Coaching', 'Education / Coaching'),
    ('Professional Services', 'Professional Services'),
    ('Home Services', 'Home Services'),
    ('Travel / Tourism', 'Travel / Tourism'),
    ('Other', 'Other'),
]

BRAND_TONE_CHOICES = [
    ('Friendly', 'Friendly'),
    ('Casual', 'Casual'),
    ('Professional', 'Professional'),
    ('Premium', 'Premium'),
    ('Approachable', 'Approachable'),
    ('Traditional', 'Traditional'),
    ('Modern', 'Modern'),
    ('Playful', 'Playful'),
    ('Formal', 'Formal'),
]

COMMUNICATION_LENGTH_CHOICES = [
    ('Short', 'Short'),
    ('Balanced', 'Balanced'),
    ('Detailed', 'Detailed'),
]

COMMUNICATION_STYLE_CHOICES = [
    ('Simple', 'Simple'),
    ('Conversational', 'Conversational'),
    ('Professional', 'Professional'),
    ('Premium', 'Premium'),
]

LANGUAGE_CHOICES = [
    ('English', 'English'),
    ('Hindi', 'Hindi'),
    ('Marathi', 'Marathi'),
    ('Gujarati', 'Gujarati'),
    ('Tamil', 'Tamil'),
    ('Telugu', 'Telugu'),
    ('Bengali', 'Bengali'),
    ('Other', 'Other'),
]

TARGET_CUSTOMER_CHOICES = [
    ('Families', 'Families'),
    ('Students', 'Students'),
    ('Professionals', 'Professionals'),
    ('Local Residents', 'Local Residents'),
    ('Tourists', 'Tourists'),
    ('Businesses', 'Businesses'),
    ('Other', 'Other'),
]


class BusinessContextForm(forms.ModelForm):
    # Admin Credentials Fields for Onboarding Creation
    admin_username = forms.CharField(
        label="Admin Username",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 placeholder-slate-400 focus:bg-white focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm shadow-sm transition-all',
            'placeholder': 'Choose an admin username (e.g. admin)',
            'autocomplete': 'username',
        })
    )
    admin_password = forms.CharField(
        label="Admin Password",
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 placeholder-slate-400 focus:bg-white focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm shadow-sm transition-all',
            'placeholder': 'Choose a strong password',
            'autocomplete': 'new-password',
        })
    )

    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        widget=forms.Select(attrs={
            "class": "w-full px-4 py-3 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 focus:bg-white focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm shadow-sm transition-all",
            "id": "id_category",
            "onchange": "toggleCategoryOther(this.value)",
        })
    )
    
    communication_length = forms.ChoiceField(
        choices=COMMUNICATION_LENGTH_CHOICES,
        widget=forms.RadioSelect(attrs={
            "class": "peer hidden",
        })
    )
    
    communication_style = forms.ChoiceField(
        choices=COMMUNICATION_STYLE_CHOICES,
        widget=forms.RadioSelect(attrs={
            "class": "peer hidden",
        })
    )

    class Meta:
        model = BusinessProfile
        fields = [
            'name', 'category', 'category_other', 'location', 'description',
            'differentiator', 'important_facts', 'custom_restrictions',
            'google_review_url', 'website', 'opening_hours',
            'business_story', 'important_terminology'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 placeholder-slate-400 focus:bg-white focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm shadow-sm transition-all',
                'placeholder': 'e.g., Lumina Dental Care',
                'required': 'required'
            }),
            'category_other': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 placeholder-slate-400 focus:bg-white focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm shadow-sm transition-all',
                'placeholder': 'Specify your category',
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 placeholder-slate-400 focus:bg-white focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm shadow-sm transition-all',
                'placeholder': 'e.g., Mumbai, India',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 placeholder-slate-400 focus:bg-white focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm shadow-sm transition-all resize-y',
                'rows': 3,
                'placeholder': 'What does your business do? Describe it in 1-2 sentences.',
                'required': 'required'
            }),
            'differentiator': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 placeholder-slate-400 focus:bg-white focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm shadow-sm transition-all resize-y',
                'rows': 3,
                'placeholder': 'What are you known for? What makes you different from other businesses?',
                'required': 'required'
            }),
            'important_facts': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 placeholder-slate-400 focus:bg-white focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm shadow-sm transition-all resize-y',
                'rows': 3,
                'placeholder': 'What important factual information should the AI know about your business?',
                'required': 'required'
            }),
            'custom_restrictions': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 placeholder-slate-400 focus:bg-white focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm shadow-sm transition-all resize-y',
                'rows': 2,
                'placeholder': 'Is there anything the AI should never claim, assume, mention, or promise about your business?'
            }),
            'google_review_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 placeholder-slate-400 focus:bg-white focus:ring-2 focus:ring-blue-600 focus:border-transparent font-mono text-sm shadow-sm transition-all',
                'placeholder': 'https://g.page/r/example/review',
                'required': 'required'
            }),
            'website': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 placeholder-slate-400 focus:bg-white focus:ring-2 focus:ring-blue-600 focus:border-transparent font-mono text-sm shadow-sm transition-all',
                'placeholder': 'https://www.yourbusiness.com'
            }),
            'opening_hours': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 placeholder-slate-400 focus:bg-white focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm shadow-sm transition-all resize-y',
                'rows': 2,
                'placeholder': 'e.g., Mon-Fri: 9am - 8pm, Sat: 10am - 6pm'
            }),
            'business_story': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 placeholder-slate-400 focus:bg-white focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm shadow-sm transition-all resize-y',
                'rows': 3,
                'placeholder': 'Optional: Share the story behind your business...'
            }),
            'important_terminology': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 placeholder-slate-400 focus:bg-white focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm shadow-sm transition-all resize-y',
                'rows': 2,
                'placeholder': 'Specific words, names, or terminology the AI should use...'
            }),
        }

    def clean_google_review_url(self):
        url = self.cleaned_data.get('google_review_url', '').strip()
        if url and not (url.startswith('http://') or url.startswith('https://')):
            raise forms.ValidationError('Please enter a valid URL starting with http:// or https://')
        return url
