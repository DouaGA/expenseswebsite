from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Count, Q, Avg, F
from django.db.models.functions import TruncDate
from datetime import timedelta
import json
import csv
from openpyxl import Workbook
from django.urls import reverse
from .models import User, Claim, ClaimType, Municipality, Profile, PostalCode
from .forms import AgentRegisterForm, CitizenRegisterForm, ClaimForm, ProfileForm
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.contrib.auth.hashers import check_password
from django.core.serializers import serialize

# Vues communes
def home(request):
    if request.user.is_authenticated:
        if request.user.user_type == 'agent':
            return redirect('core:agent_dashboard')
        else:
            return redirect('core:citizen_dashboard')
    return render(request, 'core/home.html')

class LogoutView(DjangoLogoutView):
    def get_next_page(self):
        return super().get_next_page()
    
def access_denied(request):
    required_role = request.GET.get('required', '')
    current_role = request.user.user_type if request.user.is_authenticated else ''
    
    if required_role == 'citizen' and current_role == 'agent':
        return redirect('core:agent_dashboard')
    elif required_role == 'agent' and current_role == 'citizen':
        return redirect('core:citizen_dashboard')
    
    return render(request, 'core/partials/access_denied.html', {
        'required_role': required_role,
        'current_role': current_role
    })

class StaffLoginView(View):
    def get(self, request):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect('core:staff_dashboard')
        return render(request, 'core/staff_login.html', {
            'next': request.GET.get('next', '')
        })

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next') or 'core:staff_dashboard'
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            return redirect(next_url)
        
        messages.error(request, "Identifiants invalides ou vous n'avez pas les droits administrateur.")
        return render(request, 'core/staff_login.html', {
            'username': username,
            'next': next_url
        })

@login_required
def staff_dashboard(request):
    if not request.user.is_staff:
        return redirect('core:access_denied')
    
    users_count = User.objects.count()
    agents_count = User.objects.filter(user_type='agent').count()
    citizens_count = User.objects.filter(user_type='citizen').count()
    
    return render(request, 'core/staff_dashboard.html', {
        'users_count': users_count,
        'agents_count': agents_count,
        'citizens_count': citizens_count
    })

def login_selector(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            if request.user.user_type == 'agent':
                return redirect('core:agent_dashboard')
            else:
                return redirect('core:citizen_dashboard')
        return render(request, 'core/auth/login_selector.html')
    return HttpResponseNotAllowed(['GET'])

class AgentLoginView(View):
    def get(self, request):
        if request.user.is_authenticated and request.user.user_type == 'agent':
            return redirect('core:agent_dashboard')
        return render(request, 'core/auth/agent_login.html', {
            'next': request.GET.get('next', '')
        })

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next', 'core:agent_dashboard')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.user_type == 'agent':
            login(request, user)
            return redirect(next_url)
        
        messages.error(request, "Identifiants invalides ou vous n'êtes pas un agent.")
        return render(request, 'core/auth/agent_login.html', {
            'username': username,
            'next': next_url
        })
    
class CitizenLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:citizen_dashboard')
        return render(request, 'core/auth/citizen_login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        cin = request.POST.get('cin')
        
        try:
            user = User.objects.get(email=email, cin=cin)
        except User.DoesNotExist:
            user = None
        
        if user is not None and check_password(password, user.password):
            if user.user_type == 'citizen':
                login(request, user)
                return redirect('core:citizen_dashboard')
        
        messages.error(request, "Email, CIN ou mot de passe incorrect")
        return render(request, 'core/auth/citizen_login.html')
    
class AgentRegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:agent_dashboard')
        form = AgentRegisterForm()
        return render(request, 'core/auth/agent_register.html', {'form': form})

    def post(self, request):
        form = AgentRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'agent'
            user.save()
            
            login(request, user)
            messages.success(request, "Inscription réussie ! Vous êtes maintenant connecté.")
            return redirect('core:agent_dashboard')
        
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")
        return render(request, 'core/auth/agent_register.html', {'form': form})
    
class CitizenRegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:citizen_dashboard')
        form = CitizenRegisterForm()
        return render(request, 'core/auth/citizen_register.html', {'form': form})

    def post(self, request):
        form = CitizenRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'citizen'
            user.save()
            messages.success(request, "Compte citoyen créé avec succès! Connectez-vous maintenant.")
            return redirect('core:citizen_login')
        
        return render(request, 'core/auth/citizen_register.html', {'form': form})
    
# Vues pour les agents
@login_required
def agent_dashboard(request):
    if request.user.user_type != 'agent':
        return redirect('core:access_denied')
    
    total_claims = Claim.objects.count()
    pending_count = Claim.objects.filter(status='pending').count()
    accepted_count = Claim.objects.filter(status='accepted').count()
    rejected_count = Claim.objects.filter(status='rejected').count()
    
    pending_percentage = round((pending_count / total_claims * 100)) if total_claims > 0 else 0
    accepted_percentage = round((accepted_count / total_claims * 100)) if total_claims > 0 else 0
    rejected_percentage = round((rejected_count / total_claims * 100)) if total_claims > 0 else 0
    
    pending_claims = Claim.objects.filter(status='pending').order_by('-created_at')[:5]
    accepted_claims = Claim.objects.filter(status='accepted').order_by('-created_at')[:5]
    rejected_claims = Claim.objects.filter(status='rejected').order_by('-created_at')[:5]
    
    last_30_days = timezone.now() - timedelta(days=30)
    
    daily_counts = (
        Claim.objects
        .filter(created_at__gte=last_30_days)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    
    dates = [str(day['date'].strftime('%d/%m')) for day in daily_counts]
    daily_counts_data = [day['count'] for day in daily_counts]
    
    claim_types = ClaimType.objects.annotate(count=Count('claim'))
    type_labels = [ct.name for ct in claim_types]
    type_data = [ct.count for ct in claim_types]
    
    status_labels = ['En attente', 'Acceptées', 'Rejetées']
    status_data = [pending_count, accepted_count, rejected_count]
    
    municipalities = Municipality.objects.all()
    
    has_data = total_claims > 0
    
    return render(request, 'core/agent/agent_dashboard.html', {
        'total_claims': total_claims,
        'total_pending': pending_count,
        'total_accepted': accepted_count,
        'total_rejected': rejected_count,
        'pending_percentage': pending_percentage,
        'accepted_percentage': accepted_percentage,
        'rejected_percentage': rejected_percentage,
        'pending_claims': pending_claims,
        'accepted_claims': accepted_claims,
        'rejected_claims': rejected_claims,
        'dates': json.dumps(dates),
        'daily_counts': json.dumps(daily_counts_data),
        'type_labels': json.dumps(type_labels),
        'type_data': json.dumps(type_data),
        'status_labels': json.dumps(status_labels),
        'status_data': json.dumps(status_data),
        'municipalities': municipalities,
        'has_data': has_data
    })

@login_required
def claims_list(request):
    if request.user.user_type != 'agent':
        return redirect('core:access_denied')
    
    claims = Claim.objects.all().order_by('-created_at')
    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        claims = claims.filter(status=status_filter)
    
    municipalities = Municipality.objects.all()
    
    return render(request, 'core/agent/claims_list.html', {
        'claims': claims,
        'status_filter': status_filter,
        'municipalities': municipalities
    })

@login_required
def claim_detail(request, pk):
    claim = get_object_or_404(Claim, id=pk)
    
    if request.user.user_type == 'citizen' and claim.created_by != request.user:
        return redirect('core:access_denied')
    
    municipalities = Municipality.objects.all()
    
    return render(request, 'core/agent/claim_detail.html', {
        'claim': claim,
        'municipalities': municipalities
    })

@login_required
def claims_map(request):
    if request.user.user_type != 'agent':
        return redirect('core:access_denied')
    
    claims = Claim.objects.all()
    municipalities = Municipality.objects.all()
    
    return render(request, 'core/agent/claims_map.html', {
        'claims': claims,
        'municipalities': municipalities
    })

@login_required
def export_claims(request):
    if request.user.user_type != 'agent':
        return redirect('core:access_denied')
    
    if request.method == 'POST':
        format_type = request.POST.get('format')
        status = request.POST.get('status', 'all')
        
        queryset = Claim.objects.all()
        if status != 'all':
            queryset = queryset.filter(status=status)
        
        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="claims_{status}.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['ID', 'Titre', 'Statut', 'Type', 'Municipalité', 'Date création'])
            for claim in queryset:
                writer.writerow([
                    claim.id, 
                    claim.title, 
                    claim.get_status_display(),
                    claim.claim_type.name if claim.claim_type else '',
                    claim.municipality.name if claim.municipality else '',
                    claim.created_at.strftime('%Y-%m-%d')
                ])
            return response
            
        elif format_type == 'excel':
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="claims_{status}.xlsx"'
            
            wb = Workbook()
            ws = wb.active
            ws.title = "Réclamations"
            ws.append(['ID', 'Titre', 'Statut', 'Type', 'Municipalité', 'Date création'])
            for claim in queryset:
                ws.append([
                    claim.id, 
                    claim.title, 
                    claim.get_status_display(),
                    claim.claim_type.name if claim.claim_type else '',
                    claim.municipality.name if claim.municipality else '',
                    claim.created_at.strftime('%Y-%m-%d')
                ])
            wb.save(response)
            return response
    
    return HttpResponse('Invalid request', status=400)

# Vues pour les citoyens
@login_required
def citizen_dashboard(request):
    if not hasattr(request.user, 'user_type') or request.user.user_type != 'citizen':
        return redirect(reverse('core:access_denied') + f'?required=citizen')
    
    claims = request.user.claims.all()
    stats = {
        'total': claims.count(),
        'accepted': claims.filter(status='accepted').count(),
        'pending': claims.filter(status='pending').count(),
        'rejected': claims.filter(status='rejected').count(),
    }
    
    municipalities = Municipality.objects.all()
    
    return render(request, 'core/citizen/citizen_dashboard.html', {
        'stats': stats,
        'pending_claims': Claim.objects.filter(status='pending').select_related('claim_type').defer('attachment'),     
        'accepted_claims': claims.filter(status='accepted'),
        'rejected_claims': claims.filter(status='rejected'),
        'municipalities': municipalities
    })

@login_required
def create_claim(request):
    municipalities = Municipality.objects.all().order_by('name')  # Chargement simple
    print(f"Municipalités chargées : {list(municipalities.values_list('name', flat=True))}")  # Debug

    if request.method == 'POST':
        form = ClaimForm(request.POST, request.FILES)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.created_by = request.user
            claim.save()
            return redirect('core:citizen_dashboard')
    else:
        form = ClaimForm()

    return render(request, 'core/citizen/create_claim.html', {
        'form': form,
        'municipalities': municipalities
    })

# Vues pour les profils
@login_required
def profile_view(request):
    edit_mode = request.GET.get('edit', False)
    municipalities = Municipality.objects.all()
    
    if request.method == 'POST' and edit_mode:
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('core:agent_profile')
    else:
        form = ProfileForm(instance=request.user.profile)
    
    return render(request, 'core/agent/profile.html', {
        'edit_mode': edit_mode,
        'form': form,
        'user': request.user,
        'municipalities': municipalities
    })

@login_required
def edit_profile(request):
    municipalities = Municipality.objects.all()
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('core:agent_profile')
    else:
        form = ProfileForm(instance=request.user.profile)
    
    return render(request, 'profile.html', {
        'edit_mode': True,
        'form': form,
        'user': request.user,
        'municipalities': municipalities
    })

@login_required
def stats_view(request):
    if request.user.user_type != 'agent':
        return redirect('core:access_denied')
    
    total_claims = Claim.objects.count()
    processed_claims = Claim.objects.exclude(status='pending').count()
    processing_rate = round((processed_claims / total_claims * 100)) if total_claims > 0 else 0
    rejection_rate = round((Claim.objects.filter(status='rejected').count() / total_claims * 100)) if total_claims > 0 else 0
    
    processed = Claim.objects.exclude(status='pending')
    avg_seconds = processed.aggregate(
        avg_time=Avg(F('updated_at') - F('created_at'))
    )['avg_time'] or timedelta(0)
    avg_processing_time = round(avg_seconds.total_seconds() / 3600, 1)
    
    claims_per_day = round(total_claims / 30, 1)
    
    last_30_days = timezone.now() - timedelta(days=30)
    daily_stats = (
        Claim.objects
        .filter(created_at__gte=last_30_days)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(
            pending=Count('id', filter=Q(status='pending')),
            accepted=Count('id', filter=Q(status='accepted')),
            rejected=Count('id', filter=Q(status='rejected')))
        .order_by('date')
    )
    
    status_dates = [str(day['date'].strftime('%d/%m')) for day in daily_stats]
    pending_counts = [day['pending'] for day in daily_stats]
    accepted_counts = [day['accepted'] for day in daily_stats]
    rejected_counts = [day['rejected'] for day in daily_stats]
    
    mun_stats = (
        Municipality.objects
        .annotate(count=Count('claim'))
        .order_by('-count')[:10]
    )
    municipalities = [mun.name for mun in mun_stats]
    municipality_counts = [mun.count for mun in mun_stats]
    
    recent_claims = (
        Claim.objects
        .exclude(status='pending')
        .order_by('-updated_at')[:20]
    )
    
    return render(request, 'core/agent/stats.html', {
        'processing_rate': processing_rate,
        'rejection_rate': rejection_rate,
        'avg_processing_time': avg_processing_time,
        'claims_per_day': claims_per_day,
        'status_dates': json.dumps(status_dates),
        'pending_counts': json.dumps(pending_counts),
        'accepted_counts': json.dumps(accepted_counts),
        'rejected_counts': json.dumps(rejected_counts),
        'municipalities': json.dumps(municipalities),
        'municipality_counts': json.dumps(municipality_counts),
        'recent_claims': recent_claims,
    })

@login_required
def update_claim_status(request, pk, status):
    if request.user.user_type != 'agent':
        return redirect('core:access_denied')
    
    claim = get_object_or_404(Claim, id=pk)
    
    if request.method == 'POST':
        if status in ['accepted', 'rejected', 'pending']:
            claim.status = status
            claim.updated_at = timezone.now()
            claim.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'status': status})
            
            messages.success(request, f'Statut de la réclamation mis à jour: {status}')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request'})
    
    return redirect('core:claim_detail', pk=claim.id)

def create_claim_view(request):
    existing_claims = Claim.objects.all()
    existing_claims_json = serialize('json', existing_claims)
    existing_claims_data = json.loads(existing_claims_json)
    
    simplified_claims = []
    for claim in existing_claims_data:
        simplified_claims.append({
            'title': claim['fields']['title'],
            'claim_type': claim['fields']['claim_type'],
            'description': claim['fields']['description'],
            'location_lat': claim['fields']['location_lat'],
            'location_lng': claim['fields']['location_lng']
        })
    
    municipalities = Municipality.objects.all()
    
    context = {
        'form': YourClaimForm(),
        'existing_claims_json': json.dumps(simplified_claims),
        'municipalities': municipalities
    }
    
    return render(request, 'create_claim.html', context)

def get_cites(request):
    gov = request.GET.get('gov')
    cites = PostalCode.objects.filter(gov=gov).values_list('cite', flat=True).distinct()
    return JsonResponse(list(cites), safe=False)

def example_view(request):
    gouvernorats = PostalCode.objects.values_list('gov', flat=True).distinct()
    municipalities = Municipality.objects.all()
    return render(request, 'core/example_form.html', {
        'gouvernorats': gouvernorats,
        'municipalities': municipalities
    })