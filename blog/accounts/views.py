from django.shortcuts import render, redirect
from .models import Image
from django.contrib.auth.decorators import login_required
from datetime import date

@login_required
def upload_image(request):
    if request.method == 'POST':
        if not Image.objects.filter(user=request.user, upload_date=date.today()).exists():
            image_file = request.FILES['image']
            Image.objects.create(user=request.user, image=image_file)
        return redirect('home')
    return render(request, 'images/upload.html')
