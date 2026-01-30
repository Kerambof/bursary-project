from django.shortcuts import render, redirect
from .models import Application

def apply(request):
    if request.method == "POST":
        data = request.POST

        if not data.get('full_name') or not data.get('admission_number'):
            return render(request, 'bursary/index.html', {
                'error': 'Please fill all required fields'
            })

        Application.objects.create(
            full_name=data['full_name'],
            admission_number=data['admission_number'],
            school=data['school'],
            course=data['course'],
            year_of_study=data['year_of_study'],
            phone=data['phone'],
            amount_requested=data['amount_requested']
        )
        return redirect('success')

    return render(request, 'bursary/index.html')


def success(request):
    return render(request, 'bursary/success.html')
