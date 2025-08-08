from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Count, Q, Avg, F
from django.db.models.functions import TruncDate
from datetime import timedelta
import json
import csv
from openpyxl import Workbook
from django.urls import reverse
from .models import Profile, User, Claim, ClaimType, Municipality, CodePostale, Citoyen, Agent
from .forms import AgentRegisterForm, CitoyenRegisterForm, ClaimForm, UserForm
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.contrib.auth.hashers import check_password
from django.core.serializers import serialize
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from .forms import ProfileForm

def home(request):
    return render(request, 'core/home.html')

def login_agent(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                agent = Agent.objects.get(user=user)
                login(request, user)
                request.session['agent_id'] = agent.id
                return redirect('agent_dashboard')
            except Agent.DoesNotExist:
                messages.error(request, "Ce compte n'est pas enregistré comme agent.")
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    
    return render(request, 'core/login_agent.html')

def login_citoyen(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            try:
                citoyen = Citoyen.objects.get(user=user)
                login(request, user)
                request.session['citoyen_id'] = citoyen.id
                return redirect('citizen_dashboard')
            except Citoyen.DoesNotExist:
                messages.error(request, "Ce compte n'est pas enregistré comme citoyen.")
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    
    return render(request, 'core/login_citoyen.html')

def signup_citoyen(request):
    if request.method == 'POST':
        form = CitoyenRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login_citoyen')
    else:
        form = CitoyenRegisterForm()
    return render(request, 'core/signup_citoyen.html', {'form': form})

def signup_agent(request):
    if request.method == 'POST':
        form = AgentRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login_agent')
    else:
        form = AgentRegisterForm()
    return render(request, 'core/signup_agent.html', {'form': form})


@login_required
def agent_dashboard(request):
    claims = Claim.objects.all()
    context = {
        'total_claims': claims.count(),
        'pending_claims': claims.filter(status=Claim.PENDING),
        'accepted_claims': claims.filter(status=Claim.ACCEPTED),
        'rejected_claims': claims.filter(status=Claim.REJECTED),
    }
    return render(request, 'core/agent_dashboard.html', context)

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('home')

@login_required
def claims_list(request):
    # Pour les citoyens, ne montrer que leurs propres réclamations
    if hasattr(request.user, 'citoyen'):
        claims = Claim.objects.filter(created_by=request.user).order_by('-created_at')
    # Pour les agents, montrer toutes les réclamations
    elif hasattr(request.user, 'agent'):
        claims = Claim.objects.all().order_by('-created_at')
    else:
        claims = Claim.objects.none()  # Si ni citoyen ni agent
    
    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        claims = claims.filter(status=status_filter)
    
    municipalities = Municipality.objects.all()
    
    return render(request, 'core/claims_list.html', {
        'claims': claims,
        'status_filter': status_filter,
        'municipalities': municipalities
    })

@login_required
def agent_claim_detail(request, pk):
    claim = get_object_or_404(Claim, pk=pk)
    
    # Vérification plus stricte du rôle agent
    if not hasattr(request.user, 'agent'):
        raise PermissionDenied("Accès réservé aux agents municipaux")
    
    # Gestion du changement de statut
    if request.method == 'POST' and 'status' in request.POST:
        new_status = request.POST['status']
        if new_status in [Claim.PENDING, Claim.ACCEPTED, Claim.REJECTED]:
            claim.status = new_status
            claim.updated_at = timezone.now()
            claim.save()
            messages.success(request, f"Statut mis à jour: {claim.get_status_display()}")
            return redirect('agent_claim_detail', pk=pk)
    
    return render(request, 'core/agent_claim_detail.html', {
        'claim': claim,
        'now': timezone.now()  # Utile pour les calculs de durée
    })

@login_required
def citizen_claim_detail(request, pk):
    claim = get_object_or_404(Claim, pk=pk)
    if claim.created_by != request.user:
        raise PermissionDenied 
    return render(request, 'core/citizen_claim_detail.html', {'claim': claim})

@login_required
def claims_map(request):
    claims = Claim.objects.all()
    municipalities = Municipality.objects.all()
    
    return render(request, 'core/claims_map.html', {
        'claims': claims,
        'municipalities': municipalities
    })

@login_required
def export_claims(request):
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


@login_required
def create_claim(request):
    if request.method == 'POST':
        form = ClaimForm(request.POST, request.FILES)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.created_by = request.user
            claim.status = Claim.PENDING
            claim.save()
            messages.success(request, "Réclamation créée avec succès!")
            return redirect('citizen_dashboard')
        else:
            # Affichez les erreurs spécifiques
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ClaimForm()

    return render(request, 'core/create_claim.html', {
        'form': form,
        'municipalities': Municipality.objects.all(),
        'claim_types': ClaimType.objects.filter(is_active=True),  # Seulement les types actifs
    })


@login_required
def citizen_dashboard(request):
    # Récupérer toutes les réclamations de l'utilisateur connecté
    claims = request.user.claims.all().order_by('-created_at')
    
    # Séparer par statut pour les différents onglets
    context = {
        'pending_claims': claims.filter(status=Claim.PENDING),
        'accepted_claims': claims.filter(status=Claim.ACCEPTED),
        'rejected_claims': claims.filter(status=Claim.REJECTED),
    }
    return render(request, 'core/citizen_dashboard.html', context)



@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    edit_mode = request.GET.get('edit', False)
    municipalities = Municipality.objects.all()
    
    if request.method == 'POST' and edit_mode:
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profil mis à jour avec succès!")
            return redirect('profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)
    
    return render(request, 'core/profile.html', {
        'edit_mode': edit_mode,
        'user_form': user_form,
        'profile_form': profile_form,
        'user': request.user,
        'municipalities': municipalities
    })

@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    municipalities = Municipality.objects.all()
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'core/profile.html', {
        'edit_mode': True,
        'form': form,
        'user': request.user,
        'municipalities': municipalities
    })

@login_required
def stats_view(request):
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
    
    return render(request, 'core/stats.html', {
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
    
    return redirect('agent_claim_detail', pk=claim.id)

def get_cites(request):
    gov = request.GET.get('gov')
    cites = CodePostale.objects.filter(gov=gov).values_list('cite', flat=True).distinct()
    return JsonResponse(list(cites), safe=False)

@login_required
def edit_claim(request, pk):
    claim = get_object_or_404(Claim, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = ClaimForm(request.POST, request.FILES, instance=claim)
        if form.is_valid():
            form.save()
            messages.success(request, "Réclamation mise à jour avec succès!")
            return redirect('citizen_dashboard')
    else:
        form = ClaimForm(instance=claim)
    
    return render(request, 'core/edit_claim.html', {  # Chemin correct
        'form': form,
        'claim': claim,
        'municipalities': Municipality.objects.all()
    })

@login_required
@require_POST
def delete_claim(request, pk):
    claim = get_object_or_404(Claim, pk=pk, created_by=request.user)
    claim.delete()
    messages.success(request, "Réclamation supprimée avec succès!")
    return redirect('citizen_dashboard')

@login_required
def check_user_type(request):
    return JsonResponse({
        'user_type': request.user.user_type,
        'is_authenticated': request.user.is_authenticated
    })
