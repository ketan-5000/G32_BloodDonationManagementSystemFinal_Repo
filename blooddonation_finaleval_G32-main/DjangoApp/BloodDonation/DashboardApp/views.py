from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import BloodDonation, DonationCamp, BloodRequest

@login_required
def add_camp_view(request):
    city_choices = BloodDonation.CITY_CHOICES

    if request.method == 'POST':
        camp_name = request.POST.get('camp_name')
        city = request.POST.get('city')
        date = request.POST.get('date')
        time = request.POST.get('time')
        organizer_name = request.POST.get('organizer_name')
        contact_info = request.POST.get('contact_info')

        if not all([camp_name, city, date, time, organizer_name, contact_info]):
            messages.error(request, "❌ All fields are required.")
            return redirect('add_camp')

        DonationCamp.objects.create(
            camp_name=camp_name,
            city=city,
            date=date,
            time=time,
            organizer_name=organizer_name,
            contact_info=contact_info,
            created_by=request.user
        )

        messages.success(request, "✅ Camp added successfully!")
        return redirect('dashboard')

    return render(request, 'add_camp.html', {'city_choices': city_choices})


@login_required
def search_camp_view(request):
    print(BloodDonation.CITY_CHOICES) 
    city_choices = [city for city in BloodDonation.CITY_CHOICES]

    
    selected_city = request.GET.get('city')

    if selected_city:
        camps = DonationCamp.objects.filter(city=selected_city).order_by('date')
    else:
        camps = DonationCamp.objects.all().order_by('date')

    return render(request, 'search_camp.html', {
        'camps': camps,
        'city_choices': city_choices,
        'selected_city': selected_city
    })



def is_superuser(user):
    return user.is_authenticated and user.is_superuser


@login_required
def dashboard_view(request):
    blood_groups = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
    cities = ["Delhi", "Mumbai", "Chandigarh", "Rajpura", "Ludhiana", "Bathinda", "Patiala"]

    blood_data = {
        bg: BloodDonation.objects.filter(blood_group=bg).aggregate(Sum('amount'))['amount__sum'] or 0
        for bg in blood_groups
    }

    selected_city = request.GET.get('city')
    selected_blood_group = request.GET.get('blood_group')

    filters = {}
    if selected_city:
        filters['city'] = selected_city
    if selected_blood_group:
        filters['blood_group'] = selected_blood_group

    all_recent_donations = BloodDonation.objects.filter(**filters).select_related('donor').order_by('-donation_date')

    return render(request, 'dashboard.html', {
        'blood_data': blood_data,
        'all_recent_donations': all_recent_donations,
        'city_choices': cities,
        'blood_group_choices': blood_groups,
        'selected_city': selected_city,
        'selected_blood_group': selected_blood_group,
    })

@login_required
def add_donation_view(request):
    city_choices = [city for city in BloodDonation.CITY_CHOICES]

    if request.method == 'POST':
        age = request.POST.get('age')
        weight = request.POST.get('weight')
        blood_group = request.POST.get('blood_group')
        city = request.POST.get('city')
        pints_donated = request.POST.get('pints_donated')

        if not all([age, weight, city, pints_donated, blood_group]):
            messages.error(request, "❌ All fields are required!")
            return redirect('add_donation')

        age = int(age)
        weight = float(weight)
        pints_donated = float(pints_donated)

        if age < 18:
            messages.warning(request, "❌ You must be at least 18 years old to donate blood.")
            return redirect('add_donation')
        elif weight < 50:
            messages.warning(request, "❌ You must weigh at least 50 kg to donate blood.")
            return redirect('add_donation')

        donation = BloodDonation.objects.create(
            donor=request.user,
            email=request.user.email,
            blood_group=blood_group,
            amount=pints_donated,
            city=city,
            weight=weight,
            age=age
        )

        messages.success(request, f"✅ Successfully donated {pints_donated} pints of blood!")
        return redirect('dashboard')

    return render(request, 'add_donation.html', {
        'city_choices': city_choices
    })

@login_required
def request_blood_view(request):
    blood_groups = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
    blood_data = {
        bg: BloodDonation.objects.filter(blood_group=bg).aggregate(Sum('amount'))['amount__sum'] or 0
        for bg in blood_groups
    }

    # Admin approving a request
    if request.user.is_superuser and request.method == 'POST' and 'approve_request_id' in request.POST:
        try:
            req_id = int(request.POST.get('approve_request_id'))
            req = BloodRequest.objects.get(id=req_id)

            if req.is_approved:
                messages.info(request, "ℹ️ Request already approved.")
            else:
                available = blood_data.get(req.blood_group, 0)
                if available >= req.quantity_needed:
                    # Deduct blood from available donations
                    remaining = req.quantity_needed
                    donations = BloodDonation.objects.filter(blood_group=req.blood_group).order_by('donation_date')
                    for donation in donations:
                        if remaining <= 0:
                            break
                        if donation.amount <= remaining:
                            remaining -= donation.amount
                            donation.amount = 0
                        else:
                            donation.amount -= remaining
                            remaining = 0
                        donation.save()

                    req.is_approved = True
                    req.save()
                    messages.success(request, f"✅ Approved request from {req.requester.get_full_name() or req.requester.username} for {req.blood_group}.")
                else:
                    messages.error(request, f"❌ Not enough {req.blood_group} blood available to approve this request.")
        except (BloodRequest.DoesNotExist, ValueError):
            messages.error(request, "❌ Request not found or invalid ID.")
        return redirect('request_blood')

    # Regular user submitting a blood request
    elif not request.user.is_superuser and request.method == 'POST':
        selected_blood_group = request.POST.get('blood_group')
        quantity = request.POST.get('quantity_needed')
        try:
            quantity = float(quantity)
        except (ValueError, TypeError):
            quantity = 1.0

        if selected_blood_group:
            BloodRequest.objects.create(
                requester=request.user,
                blood_group=selected_blood_group,
                quantity_needed=quantity,
            )
            messages.success(request, f"✅ Your request for {selected_blood_group} has been submitted.")
        else:
            messages.error(request, "❌ Invalid blood group.")

    pending_requests = BloodRequest.objects.filter(is_approved=False) if request.user.is_superuser else None

    return render(request, 'request_blood.html', {
        'blood_data': blood_data,
        'pending_requests': pending_requests,
    })