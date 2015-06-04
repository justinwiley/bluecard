from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.template import RequestContext
from django.http import *
from django.core.urlresolvers import reverse
from django.db.models import Q      # sql sanitization for custom queries
from .models import Customer, Document
from .forms import CustomerForm, UploadForm
import requests, json
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('config/config.cnf')

def login_user(request):
    "Login to the app"
    logout(request)
    username = password = ''
    if request.POST:
        # pdb.set_trace()
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
    return render_to_response('users/login.html', context_instance=RequestContext(request))

def logout_user(request):
    "Logout of the app"
    logout(request)
    return HttpResponseRedirect('/login')

@login_required(login_url='/login/')
def index(request):
    "Show all customers"
    cs = Customer.objects.order_by('name')
    context = {'cs': cs}
    return render(request, 'customers/index.html', context)

@login_required(login_url='/login/')
def new(request):
    "Create new customer"
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            c = Customer(name=form.cleaned_data['name'])
            c.save()
            messages.add_message(request, messages.INFO, 'New customer created.')
            return HttpResponseRedirect('/')
    else:
        context = {
            'form': CustomerForm()
        }
        return render(request, 'customers/new.html', context)


@login_required(login_url='/login/')
def customer(request, customer_id):
    "View or update customer"
    c = get_object_or_404(Customer, pk=customer_id)

    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            c.name = form.cleaned_data['name']
            c.save()
            messages.add_message(request, messages.INFO, 'Customer updated.')

            return HttpResponseRedirect('/')
    else:
        context = {
            'customer': c,
            'form': CustomerForm(initial = {'name': c.name})
        }
        return render(request, 'customers/edit.html', context)

@login_required(login_url='/login/')
def upload(request, customer_id):
    "Upload a new document for processing"
    c = get_object_or_404(Customer, pk=customer_id)

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            print "valid"
            i = Document(image=request.FILES['file'], customer_id=c.id)
            i.save()
            messages.add_message(request, messages.INFO, 'Sucessfully imported ID, it will be processed shortly.')
            context = {'customer': c, 'imports': c.document_set.all()}
            return render(request, 'customers/imports.html', context)
        else:
            print "not valid"
            context = {'customer': c, 'form': UploadForm()}
            return render(request, 'customers/upload.html', context)
    else:
        context = {'customer': c, 'form': UploadForm()}
        return render(request, 'customers/upload.html', context)

@login_required(login_url='/login/')
def imports(request, customer_id):
    "Display all imported documents"
    c = get_object_or_404(Customer, pk=customer_id)

    context = {'customer': c, 'imports': c.document_set.all()}
    return render(request, 'customers/imports.html', context)

def status(request, customer_id):
    "Checks status of all documents associated with the customer by pinging Captricity"

    c = get_object_or_404(Customer, pk=customer_id)
    ds = c.document_set.exclude(Q(status='imported') | Q(status='finished'))

    for document in ds:
        job_id = document.job_id
        url = 'https://shreddr.captricity.com/api/v1/job/'+str(job_id)+'/instance-set/'
        print "requesting: " + url
        headers = {
            'user-agent': 'bluecard/0.0.1',
            'Captricity-API-Token': config.get('captricity', 'apitoken')}
        r = requests.get(url, headers=headers)
        instance_set_id = json.loads(r.text)[0]['id']
        shred_url = "https://shreddr.captricity.com/api/v1/instance-set/"+str(instance_set_id)+"/shred/"
        print "finding shred: " + shred_url
        shreds = json.loads(r.text)

    messages.add_message(request, messages.INFO, 'Status updated.')
    context = {'customer': c, 'imports': c.document_set.all()}
    return HttpResponseRedirect("/customers/"+str(c.id)+"/imports")
