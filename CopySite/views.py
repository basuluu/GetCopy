from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth.models import User
from .copysite import *
from .models import File
from threading import Thread
import os


# Create your views here.
def home(request):
    if request.method == "POST":

        if not request.user.is_authenticated:
            return redirect('/login/')

        url = request.POST['url']
        download_method = request.POST['downloadMethod']

        if not url.startswith('http'):
            url = 'http://' + url
 
        file = File.objects.create(user=request.user, url=url, method=download_method, ready=False)
        thread1 = Thread(target=main, args=(url, download_method, file,))
        thread1.start()   
        return redirect('/')
    try:
        history = File.objects.filter(user=request.user).order_by('-pk')
        for story in history:
            story.file = 'download/' + story.file
    except:
        history = {}
    return render(request, 'home.html', 
        {'history': dict(zip(range(len(history),-1,-1), history))})

def get_history(request):
    try:
        history = File.objects.filter(user=request.user).order_by('-pk')
        for story in history:
            story.file = 'download/' + story.file
    except:
        history = {}
    return render(request, 'only_url_table.html', 
        {'history': dict(zip(range(len(history),-1,-1), history))})

def download_zip(request, file_path):
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/zip")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404