from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import DirectoryCreate, FileCreate, tab_options
from .models import Directory, File, User
from .utils import disableChildren, createSections, addExtra, runFrama, getResult, parseCompilation, addLineNumbers
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.utils import timezone
from django.http import JsonResponse
import os

OVERLAP = "overlap"
ACTIVE = "overlap-active"

overlaps_mapping = {
    "none": [OVERLAP, OVERLAP, OVERLAP],
    "prover": [ACTIVE, OVERLAP, OVERLAP],
    "vcs": [OVERLAP, ACTIVE, OVERLAP],
    "result": [OVERLAP, OVERLAP, ACTIVE]
}

@login_required(login_url='/login/')
def index(request):
    try:
        all_dire = Directory.objects.filter(availability=True, owner__login=request.user.username).order_by('path')
    except:
        return render(request, "index/index.html")

    context = { 
        'all_dire' : all_dire,
        'content' : "Choose a file!",
        'frama' : [],
        'tab' : "",
        'overlaps' : overlaps_mapping.get("none"), #no tabs are active
        'theme' : request.session.get("theme")
    }
    request.session["prev"] = -1 #indicate that there was no previous file chosen
    return render(request, "index/index.html", context)

@login_required(login_url='/login/')
def directoryCreate(request):
    form = DirectoryCreate(request.POST or None)
    form.fields["parentDirectory"].queryset = Directory.objects.filter(availability=True, owner__login=request.user.username)
    if form.is_valid():
        dire = form.save(commit=False)
        dire = addExtra(dire, request.user.username)
        dire.save()
        return HttpResponseRedirect('/index/')

    context = {
        'form': form,
        'theme' : request.session.get("theme")
    }
    return render(request, "index/create.html", context)

@login_required(login_url='/login/')
def fileCreate(request):
    if request.method == "POST":
        form = FileCreate(request.POST or None, request.FILES)
        form.fields["directory"].queryset = Directory.objects.filter(availability=True, owner__login=request.user.username)
        if form.is_valid():
            f = form.save()
            createSections(f)
            return HttpResponseRedirect('/index/')
    else:
        form = FileCreate()
        form.fields["directory"].queryset = Directory.objects.filter(availability=True, owner__login=request.user.username)
    context = {
        'form' : form,
        'theme' : request.session.get("theme")
    }
    return render(request, "index/create.html", context)

@login_required(login_url='/login/')
def deletionView(request):
    try:
        all_dire = Directory.objects.filter(availability=True, owner__login=request.user.username)
    except:
        return render(request, "index/delete.html")

    context = {'all_dire' : all_dire}
    return render(request, "index/delete.html", context)

@login_required(login_url='/login/')
def directoryDelete(request, pk):
    dire = get_object_or_404(Directory, pk=pk)
    disableChildren(dire)

    return HttpResponseRedirect('/index/')

@login_required(login_url='/login/')
def fileDelete(request, pk):
    f = get_object_or_404(File, pk=pk)
    f.availability = False
    f.save()

    return HttpResponseRedirect('/index/')

@login_required(login_url='/login/')
def showFile(request, pk):
    f = get_object_or_404(File, pk=pk)
    filePath = f.ffile.path

    #reset previously selected compilation options
    request.session['prover'] = "None"
    request.session['rte'] = "No"
    request.session['vc'] = "None"

    with open(filePath, 'r') as currFile:
        content = list(currFile)
    content = addLineNumbers(content)
    frama, advanced = runFrama(filePath, "None", "No", "None")
    parsed = parseCompilation(frama, f.sections.all(), advanced, request.user.username)
    all_dire = Directory.objects.filter(availability=True, owner__login=request.user.username).order_by("path")

    request.session["prev"] = pk
    lastSession = {
        'content' : content,
        'parsedFrama' : parsed
    }
    request.session[str(pk)] = lastSession
    context = {
        'all_dire' : all_dire,
        'content' : content,
        'frama' : parsed,
        'tab' : "",
        'overlaps' : overlaps_mapping.get("none"),
        'theme' : request.session.get("theme")
    }
    return render(request, "index/index.html", context)

@login_required(login_url='/login/')
def showTab(request, tab):
    pk = str(request.session.get("prev"))
    if (pk == "-1"): #no file case
        return HttpResponseRedirect('/index/')

    lastSession = request.session.get(pk)
    all_dire = Directory.objects.filter(availability=True, owner__login=request.user.username).order_by("path")
    extra = ""
    overlaps = overlaps_mapping.get(tab)
    if tab == "result" and request.session.get(pk + "extra") is None:
        f = get_object_or_404(File, pk=int(pk))
        filePath = f.ffile.path
        extra = getResult(filePath)
        lastSession['extra'] = extra
        request.session[pk + "extra"] = extra

    context = {
        'all_dire' : all_dire,
        'content' : lastSession.get('content'),
        'frama' : lastSession.get('parsedFrama'),
        'tab' : tab,
        'extra' : extra,
        'overlaps' : overlaps,
        'compOptions' : tab_options.get(tab),
        'theme' : request.session.get("theme")
    }
    return render(request, "index/index.html", context)

@login_required(login_url='/login/')
def saveProver(request):
    if request.method == 'POST':
        selected = request.POST.get('provers')
        if selected != None:
            request.session["prover"] = selected

    return redirect('showTab', tab="prover")

@login_required(login_url='/login/')
def saveVc(request):
    if request.method == 'POST':
        selectedRte = request.POST.get('rte')
        if selectedRte != None:
            request.session["rte"] = selectedRte
        selectedVc = request.POST.get('vcs')
        if selectedVc != None:
            request.session["vc"] = selectedVc
            
    return redirect('showTab', tab="vcs")

@login_required(login_url='/login/')
def compile(request):
    pk = str(request.session.get("prev"))
    if (pk == "-1"): #no file case
        return HttpResponseRedirect('/index/')

    lastSession = request.session.get(pk)
    all_dire = Directory.objects.filter(availability=True, owner__login=request.user.username).order_by("path")
    f = get_object_or_404(File, pk=pk)
    fpath = f.ffile.path
    
    frama, advanced = runFrama(fpath, request.session.get('prover'), request.session.get('rte'), request.session.get('vc')) #run command with options
    parsed = parseCompilation(frama, f.sections.all(), advanced, request.user.username) 
    lastSession['parsedFrama'] = parsed
    request.session[pk] = lastSession

    context = {
        'all_dire' : all_dire,
        'content' : lastSession.get('content'),
        'frama' : parsed,
        'tab' : "",
        'overlaps' : ["overlap", "overlap", "overlap"], #no tabs are active
        'theme' : request.session.get("theme")
    }
    return render(request, "index/index.html", context)

@login_required(login_url='/login/')
def logout(request):
    auth.logout(request)
    return render(request, "registration/logout.html")

@login_required(login_url='/login/')
def preindex(request):
    request.session["theme"] = "normal-color"
    currentUser = request.user
    userObj = User.objects.filter(login=currentUser.username)
    if not userObj:
        userObj = User.objects.create (
        name=currentUser.username,
        login=currentUser.username,
        password=currentUser.password,
        lastUpdated=timezone.now(),
        validity=True
        )
        userObj.save()
        
    return HttpResponseRedirect('/index/')

def showFileJS(request):
    pk = request.GET.get('pk', None)
    f = get_object_or_404(File, pk=pk)
    filePath = f.ffile.path

    #reset previously selected compilation options
    request.session['prover'] = "None"
    request.session['rte'] = "No"
    request.session['vc'] = "None"

    with open(filePath, 'r') as currFile:
        content = list(currFile)
    content = addLineNumbers(content)
    frama, advanced = runFrama(filePath, "None", "No", "None")
    parsed = parseCompilation(frama, f.sections.all(), advanced, request.user.username)
    all_dire = Directory.objects.filter(availability=True, owner__login=request.user.username).order_by("path")

    request.session["prev"] = pk
    lastSession = {
        'content' : content,
        'parsedFrama' : parsed
    }
    request.session[str(pk)] = lastSession
    data = {
        'content' : content,
        'frama' : parsed,
    }
    return JsonResponse(data)

def compileJS(request):
    pk = str(request.session.get("prev"))
    data = {'frama' : ""}
    if (pk == "-1"): #no file case
        return JsonResponse(data)

    lastSession = request.session.get(pk)
    f = get_object_or_404(File, pk=pk)
    fpath = f.ffile.path
    
    frama, advanced = runFrama(fpath, request.session.get('prover'), request.session.get('rte'), request.session.get('vc')) #run command with options
    parsed = parseCompilation(frama, f.sections.all(), advanced, request.user.username) 
    lastSession['parsedFrama'] = parsed
    request.session[pk] = lastSession

    data = {
        'frama' : parsed,
    }
    return JsonResponse(data)

def deleteJS(request):
    data = { 
        'all_dire' : [], 
        'all_files' : []
    }
    try:
        all_dire = Directory.objects.filter(availability=True, owner__login=request.user.username)
    except:
        return JsonResponse(data)

    request.session['prev'] = -1

    dirs = []
    files = []
    for dire in all_dire:
        dirobj = (getattr(dire, "name"), getattr(dire, "pk")) 
        dirs.append(dirobj)
        arr = []
        for f in dire.files.all():
            filobj = (getattr(f, "name"), getattr(f, "availability"), getattr(f, "pk"))
            arr.append(filobj)
        files.append(arr)

    data = {
        'all_dire' : dirs,
        'all_files' : files
    }
    return JsonResponse(data)

def deleteFileJS(request):
    pk = request.GET.get('pk', None)
    f = get_object_or_404(File, pk=pk)
    f.availability = False
    f.save()
    data = {}

    return JsonResponse(data)

def deleteDirJS(request):
    pk = request.GET.get('pk', None)
    dire = get_object_or_404(Directory, pk=pk)
    todelete = disableChildren(dire)
    data = {
        'dirpk' : todelete[0],
        'filepk' : todelete[1]
    }

    return JsonResponse(data)

def changeThemeJS(request):
    request.session["theme"] = request.GET.get('theme', "normal-color")
    data = {}
    return JsonResponse(data)

