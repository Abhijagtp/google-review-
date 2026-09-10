from django.urls import path
from . import views

app_name = 'business'

urlpatterns = [
    path('installer/', views.installer_view, name='installer'),
    path('installer/test/', views.test_connection_partial, name='test_connection'),
    path('create-admin/', views.create_admin_view, name='create_admin'),
    path('setup/', views.onboarding_view, name='onboarding'),
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('logout/', views.admin_logout_view, name='admin_logout'),
    path('ai-setup/', views.byok_setup_view, name='byok_setup'),
    path('ai-setup/test/', views.byok_test_key_partial, name='test_ai_key'),
    path('ai-setup/rollback/<int:history_id>/', views.rollback_key_view, name='rollback_key'),
    path('ai-setup/revoke/<int:history_id>/', views.revoke_key_view, name='revoke_key'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    path('dashboard/generate-preview/', views.generate_review_preview_partial, name='generate_preview'),
    path('dashboard/resolve-feedback/<int:feedback_id>/', views.resolve_private_feedback_partial, name='resolve_feedback'),
    path('review/', views.customer_review_view, name='customer_review'),
    path('review/generate/', views.generate_customer_reviews_partial, name='generate_customer_reviews'),
    path('review/submit-private-feedback/', views.submit_private_feedback_partial, name='submit_private_feedback'),
    path('review/track-copy/', views.track_copy_redirect_partial, name='track_copy'),
    path('health/', views.health_check_view, name='health_check'),
    path('ping/', views.health_check_view, name='ping'),
]

