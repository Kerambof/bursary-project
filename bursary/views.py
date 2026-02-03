from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import ApplicationForm
from .models import Constituency

def apply(request):
    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('success')
    else:
        form = ApplicationForm()
    return render(request, 'bursary/index.html', {'form': form})

def success(request):
    return render(request, 'bursary/success.html')

# AJAX call to load constituencies based on selected county
def load_constituencies(request):
    county_id = request.GET.get('county')
    constituencies = Constituency.objects.filter(county_id=county_id).all()
    return JsonResponse(list(constituencies.values('id', 'name')), safe=False)
