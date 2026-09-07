import json
import io
import qrcode
import qrcode.image.svg
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import (
    DatabaseInstallerForm,
    BusinessContextForm,
    AIConfigForm,
    AdminLoginForm,
    BRAND_TONE_CHOICES,
    LANGUAGE_CHOICES,
    TARGET_CUSTOMER_CHOICES,
)
from .installer import (
    test_database_connection,
    update_env_database_url,
    run_database_migrations,
    is_database_configured,
)
from .models import BusinessProfile, AIConfig, AIKeyHistory, default_ai_restrictions
from .key_security import encrypt_key, decrypt_key, mask_key
from .ai_engine import verify_ai_api_key, generate_ai_review_suggestion, generate_multi_review_options
from .review_helpers import get_category_config


def generate_qr_code_svg(url: str) -> str:
    """
    Generates a clean SVG string for a given URL using qrcode library.
    """
    try:
        factory = qrcode.image.svg.SvgPathImage
        img = qrcode.make(url, image_factory=factory)
        stream = io.BytesIO()
        img.save(stream)
        svg_text = stream.getvalue().decode('utf-8')
        return svg_text
    except Exception:
        return ""



def root_view(request):
    """
    Main root entry point router.
    """
    if not is_database_configured():
        return redirect("business:installer")

    try:
        profile = BusinessProfile.objects.first()
        if not profile or not profile.is_configured:
            return redirect("business:onboarding")
    except Exception:
        return redirect("business:onboarding")

    if request.user.is_authenticated:
        return redirect("business:dashboard")
    
    return redirect("business:admin_login")


def admin_login_view(request):
    """
    Admin Login View (/admin-login/).
    """
    if not is_database_configured():
        return redirect("business:installer")

    if request.user.is_authenticated:
        return redirect("business:dashboard")

    form = AdminLoginForm()
    error_message = None

    if request.method == "POST":
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"].strip()
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("business:dashboard")
            else:
                error_message = "Invalid username or password. Please try again."

    return render(request, "business/admin_login.html", {
        "form": form,
        "error_message": error_message,
    })


def admin_logout_view(request):
    """
    Admin Logout View (/logout/).
    """
    logout(request)
    return redirect("business:admin_login")


def installer_view(request):
    """
    Step 0: Web Installer View.
    """
    if is_database_configured():
        return redirect("business:onboarding")

    form = DatabaseInstallerForm()

    if request.method == "POST":
        form = DatabaseInstallerForm(request.POST)
        if form.is_valid():
            db_url = form.cleaned_data["database_url"].strip()

            success, err_msg = test_database_connection(db_url)
            if not success:
                if request.headers.get("HX-Request"):
                    return render(request, "business/partials/installer_response.html", {
                        "success": False,
                        "message": f"Connection Error: {err_msg}",
                    })
                return render(request, "business/installer.html", {
                    "form": form,
                    "error_message": err_msg,
                    "db_configured": False,
                })

            if not update_env_database_url(db_url):
                err_msg = "Could not write DATABASE_URL to .env file."
                if request.headers.get("HX-Request"):
                    return render(request, "business/partials/installer_response.html", {
                        "success": False,
                        "message": err_msg,
                    })
                return render(request, "business/installer.html", {
                    "form": form,
                    "error_message": err_msg,
                    "db_configured": False,
                })

            mig_success, mig_msg = run_database_migrations()
            if not mig_success:
                if request.headers.get("HX-Request"):
                    return render(request, "business/partials/installer_response.html", {
                        "success": False,
                        "message": f"Database connected, but migration failed: {mig_msg}",
                    })
                return render(request, "business/installer.html", {
                    "form": form,
                    "error_message": mig_msg,
                    "db_configured": False,
                })

            if request.headers.get("HX-Request"):
                response = HttpResponse(status=200)
                response["HX-Redirect"] = "/setup/"
                return response

            return redirect("business:onboarding")

    return render(request, "business/installer.html", {
        "form": form,
        "db_configured": False,
    })


def test_connection_partial(request):
    """
    HTMX endpoint to test database connection without saving.
    """
    if request.method == "POST":
        db_url = request.POST.get("database_url", "").strip()
        success, err_msg = test_database_connection(db_url)
        if success:
            return HttpResponse(
                '<div class="p-4 mb-6 text-sm text-emerald-900 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center gap-3 shadow-sm">'
                '<div class="w-7 h-7 rounded-lg bg-emerald-600 text-white flex items-center justify-center shrink-0">'
                '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"></path></svg>'
                '</div>'
                '<div>'
                '<p class="font-bold text-slate-900 text-sm">Connection Successful</p>'
                '<p class="text-slate-600 text-xs mt-0.5">Neon PostgreSQL database is online and reachable.</p>'
                '</div>'
                '</div>'
            )
        else:
            return HttpResponse(
                f'<div class="p-4 mb-6 text-sm text-rose-900 bg-rose-50 border border-rose-200 rounded-xl flex items-center gap-3 shadow-sm">'
                f'<div class="w-7 h-7 rounded-lg bg-rose-600 text-white flex items-center justify-center shrink-0">'
                f'<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
                f'</div>'
                f'<div>'
                f'<p class="font-bold text-slate-900 text-sm">Connection Error</p>'
                f'<p class="text-rose-700 text-xs mt-0.5">{err_msg}</p>'
                f'</div>'
                f'</div>'
            )
    return HttpResponse("")


def onboarding_view(request):
    """
    Step 1: Business AI Context Setup View.
    """
    if not is_database_configured():
        return redirect("business:installer")

    profile = BusinessProfile.objects.first() or BusinessProfile()

    if request.method == "POST":
        form = BusinessContextForm(request.POST, instance=profile)
        
        brand_tone = request.POST.getlist("brand_tone")
        preferred_languages = request.POST.getlist("preferred_languages")
        target_customers = request.POST.getlist("target_customers")
        
        products_json = request.POST.get("products_services_data", "[]")
        try:
            products_services = json.loads(products_json)
        except Exception:
            products_services = []

        specialty_json = request.POST.get("specialty_products_data", "[]")
        try:
            main_specialty_products = json.loads(specialty_json)
        except Exception:
            main_specialty_products = []

        faqs_json = request.POST.get("faqs_data", "[]")
        try:
            faqs = json.loads(faqs_json)
        except Exception:
            faqs = []

        admin_uname = request.POST.get("admin_username", "").strip()
        admin_pwd = request.POST.get("admin_password", "").strip()

        if form.is_valid():
            obj = form.save(commit=False)
            obj.brand_tone = brand_tone
            obj.preferred_languages = preferred_languages
            obj.target_customers = target_customers
            obj.products_services = products_services
            obj.main_specialty_products = main_specialty_products
            obj.faqs = faqs
            obj.default_ai_rules = default_ai_restrictions()
            obj.is_configured = True
            obj.save()

            if admin_uname and admin_pwd:
                user, created = User.objects.get_or_create(username=admin_uname)
                user.set_password(admin_pwd)
                user.is_staff = True
                user.is_superuser = True
                user.save()
                login(request, user)

            return redirect("business:byok_setup")
    else:
        form = BusinessContextForm(instance=profile)

    return render(request, "business/onboarding.html", {
        "form": form,
        "profile": profile,
        "brand_tone_choices": [c[0] for c in BRAND_TONE_CHOICES],
        "language_choices": [c[0] for c in LANGUAGE_CHOICES],
        "target_customer_choices": [c[0] for c in TARGET_CUSTOMER_CHOICES],
        "default_ai_rules": default_ai_restrictions(),
    })


@login_required(login_url='/admin-login/')
def byok_setup_view(request):
    """
    Step 3: BYOK AI Setup View (Protected).
    Includes API Key History Audit Trail & AES-256 Encryption.
    """
    if not is_database_configured():
        return redirect("business:installer")

    profile = BusinessProfile.objects.first()
    if not profile or not profile.is_configured:
        return redirect("business:onboarding")

    ai_config = getattr(profile, "ai_config", None) or AIConfig(business=profile)

    if request.method == "POST":
        form = AIConfigForm(request.POST, instance=ai_config)
        if form.is_valid():
            config_obj = form.save(commit=False)
            config_obj.business = profile
            
            decrypted_key = config_obj.decrypted_api_key
            is_valid, msg = verify_ai_api_key(config_obj.provider, decrypted_key, config_obj.model_name)
            config_obj.is_active = is_valid
            config_obj.save()

            # Create Key History Audit Record
            profile.key_history.filter(status='active').update(status='archived')
            AIKeyHistory.objects.create(
                business=profile,
                provider=config_obj.provider,
                encrypted_api_key=config_obj.api_key,
                masked_key=config_obj.masked_api_key,
                model_name=config_obj.model_name,
                status='active' if is_valid else 'archived',
                note=f"Key updated by admin. Verification status: {msg}"
            )

            if request.headers.get("HX-Request"):
                response = HttpResponse(status=200)
                response["HX-Redirect"] = "/dashboard/"
                return response

            return redirect("business:dashboard")
    else:
        form = AIConfigForm(instance=ai_config)

    key_history = profile.key_history.all()[:15]

    return render(request, "business/byok_setup.html", {
        "form": form,
        "profile": profile,
        "ai_config": ai_config,
        "key_history": key_history,
    })


def byok_test_key_partial(request):
    """
    HTMX partial to test API key live.
    """
    if request.method == "POST":
        provider = request.POST.get("provider", "gemini")
        api_key_input = request.POST.get("api_key", "").strip()
        model_name = request.POST.get("model_name", "").strip()

        # If key input is masked preview, decrypt original key from database
        if '••••' in api_key_input:
            profile = BusinessProfile.objects.first()
            if profile and getattr(profile, 'ai_config', None):
                api_key_input = profile.ai_config.decrypted_api_key

        is_valid, msg = verify_ai_api_key(provider, api_key_input, model_name)
        if is_valid:
            return HttpResponse(
                '<div class="p-4 mb-6 text-sm text-emerald-900 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center gap-3 shadow-sm">'
                '<div class="w-7 h-7 rounded-lg bg-emerald-600 text-white flex items-center justify-center shrink-0">'
                '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"></path></svg>'
                '</div>'
                '<div>'
                '<p class="font-bold text-slate-900 text-sm">Key Verified & Active</p>'
                f'<p class="text-slate-600 text-xs mt-0.5">{msg}</p>'
                '</div>'
                '</div>'
            )
        else:
            return HttpResponse(
                f'<div class="p-4 mb-6 text-sm text-rose-900 bg-rose-50 border border-rose-200 rounded-xl flex items-center gap-3 shadow-sm">'
                f'<div class="w-7 h-7 rounded-lg bg-rose-600 text-white flex items-center justify-center shrink-0">'
                f'<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
                f'</div>'
                f'<div>'
                f'<p class="font-bold text-slate-900 text-sm">Verification Failed</p>'
                f'<p class="text-rose-700 text-xs mt-0.5">{msg}</p>'
                f'</div>'
                f'</div>'
            )
    return HttpResponse("")


@login_required(login_url='/admin-login/')
def rollback_key_view(request, history_id):
    """
    1-Click Rollback endpoint to restore a previous API Key from history.
    """
    profile = BusinessProfile.objects.first()
    if not profile:
        return redirect("business:byok_setup")

    try:
        item = AIKeyHistory.objects.get(id=history_id, business=profile)
        profile.key_history.filter(status='active').update(status='archived')
        item.status = 'active'
        item.note = 'Restored by admin'
        item.save()

        ai_config = getattr(profile, 'ai_config', None) or AIConfig(business=profile)
        ai_config.provider = item.provider
        ai_config.api_key = item.encrypted_api_key
        ai_config.model_name = item.model_name
        
        is_valid, _ = verify_ai_api_key(item.provider, item.decrypted_api_key, item.model_name)
        ai_config.is_active = is_valid
        ai_config.save()
    except Exception:
        pass

    return redirect("business:byok_setup")


@login_required(login_url='/admin-login/')
def revoke_key_view(request, history_id):
    """
    Revoke a compromised or old API Key endpoint.
    """
    profile = BusinessProfile.objects.first()
    if profile:
        try:
            item = AIKeyHistory.objects.get(id=history_id, business=profile)
            was_active = (item.status == 'active')
            item.status = 'revoked'
            item.note = 'Revoked by admin'
            item.save()

            if was_active and getattr(profile, 'ai_config', None):
                profile.ai_config.is_active = False
                profile.ai_config.save()
        except Exception:
            pass

    return redirect("business:byok_setup")



@login_required(login_url='/admin-login/')
def dashboard_view(request):
    """
    Step 4: Business Admin Dashboard (Protected).
    Dynamic analytics tracking and real QR Code generator.
    """
    if not is_database_configured():
        return redirect("business:installer")

    profile = BusinessProfile.objects.first()
    if not profile or not profile.is_configured:
        return redirect("business:onboarding")

    ai_config = getattr(profile, "ai_config", None)

    host = request.get_host()
    review_url = f"http://{host}/review/"

    # Generate real SVG QR Code
    qr_code_svg = generate_qr_code_svg(review_url)

    # Conversion Rate
    conversion_rate = 0.0
    if profile.total_views > 0:
        conversion_rate = round((profile.total_copies_redirects / profile.total_views) * 100, 1)

    return render(request, "business/dashboard.html", {
        "profile": profile,
        "ai_config": ai_config,
        "review_url": review_url,
        "qr_code_svg": qr_code_svg,
        "conversion_rate": conversion_rate,
    })


@login_required(login_url='/admin-login/')
def generate_review_preview_partial(request):
    """
    HTMX partial for the Admin Dashboard Live AI Playground.
    """
    profile = BusinessProfile.objects.first()
    if not profile:
        return HttpResponse('<p class="text-rose-600 text-xs">Profile not found.</p>')

    highlights = request.POST.getlist("highlights")
    suggestion = generate_ai_review_suggestion(profile, highlights)

    return HttpResponse(
        f'<div class="p-4 bg-slate-900 text-white rounded-xl border border-slate-800 text-sm leading-relaxed shadow-inner animate-fade-in relative group">'
        f'<p class="font-sans font-medium text-slate-200">"{suggestion}"</p>'
        f'<div class="mt-3 flex items-center justify-between pt-3 border-t border-slate-800 text-xs text-slate-400">'
        f'<span>AI Suggestion generated via {profile.name} Context</span>'
        f'<button type="button" onclick="navigator.clipboard.writeText(\'{suggestion}\'); alert(\'Copied to clipboard!\');" class="px-2.5 py-1 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-md shadow-sm transition-all flex items-center gap-1">'
        f'<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>'
        f'Copy Text</button>'
        f'</div>'
        f'</div>'
    )


def customer_review_view(request):
    """
    Public Customer Review Page (/review/) — 100% PUBLIC.
    Tracks dynamic customer page views.
    """
    if not is_database_configured():
        return redirect("business:installer")

    profile = BusinessProfile.objects.first()
    if not profile or not profile.is_configured:
        return render(request, "business/setup_pending.html")

    # Increment total_views metric dynamically
    profile.total_views += 1
    profile.save(update_fields=['total_views'])


    cat_config = get_category_config(profile.category)

    return render(request, "business/customer_review.html", {
        "profile": profile,
        "enjoyment_options": cat_config["enjoyment_options"],
        "order_label": cat_config["order_label"],
        "order_placeholder": cat_config["order_placeholder"],
    })


def generate_customer_reviews_partial(request):
    """
    HTMX partial handling customer review generation — 100% PUBLIC.
    Tracks dynamic AI generation count.
    """
    profile = BusinessProfile.objects.first()
    if not profile:
        return HttpResponse('<p class="text-rose-600">Error loading business profile.</p>')

    # Increment total_ai_generated metric dynamically
    profile.total_ai_generated += 1
    profile.save(update_fields=['total_ai_generated'])

    enjoyment_chips = request.POST.getlist("enjoyed")
    item_used = request.POST.get("item_used", "").strip()
    stood_out = request.POST.get("stood_out", "").strip()

    options = generate_multi_review_options(profile, enjoyment_chips, item_used, stood_out)

    return render(request, "business/partials/customer_review_options.html", {
        "profile": profile,
        "options": options,
        "google_review_url": profile.google_review_url,
    })


def track_copy_redirect_partial(request):
    """
    HTMX / JS endpoint tracking dynamic copy & redirect actions.
    """
    profile = BusinessProfile.objects.first()
    if profile:
        profile.total_copies_redirects += 1
        profile.save(update_fields=['total_copies_redirects'])
    return HttpResponse("OK")
