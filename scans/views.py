from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.conf import settings
from django.db import connection
from tld import get_tld
from django.contrib.auth import logout 
from libnmap.parser import NmapParser

from django.contrib.auth.models import User
from .models import Collection, Host, Port, Filexml
from .forms import CollectionForm, UploadFile, toRegister

def register(request):
    if request.method == 'POST':
        form = toRegister(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            user = User.objects.create_user(username,email,password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            return render(request, 'scanhub/collections.html',{})
    else:
        form = toRegister()
    data = { 'form': form }
    return render(request, 'scanhub/register.html',{'form':form})

def index(request):
    return render(request, 'scanhub/index.html', {})

@login_required(login_url="/login/")
def dashboard(request):
    return render(request, 'scanhub/dashboard.html', {})

@login_required(login_url="/login/")
def collection(request):
    collections = Collection.objects.filter(owner_id = request.user.id).all()
    return render(request, 'scanhub/collection.html', {'collections':collections})

@login_required(login_url="/login/")
def collectionid(request, c_id):
    if Collection.objects.filter(id=c_id, owner_id=request.user.id).exists():
        c = Collection.objects.get(id=c_id)
        q = 'select sf.id, sf.file_size, uploaded_at, count(sh.file_id) as cont from scans_filexml as sf, scans_host as sh where owner_file_id = '+c_id+' and sf.id=sh.file_id group by sh.file_id, sf.id'
        f = Filexml.objects.raw(q)
        return render(request, 'scanhub/collectionid.html', {'collection':c, 'files':f})
    else:
        return render(request, 'scanhub/dashboard.html',{})

@login_required(login_url="/login/")
def collection_upload(request, v_id):
    if request.POST:
        form = UploadFile(request.POST, request.FILES)
        if form.is_valid():
            filexml = form.save(commit=False)
            filexml.owner_file = Collection.objects.get(id=v_id)
            filexml.file_size = 1
            name_file = settings.MEDIA_ROOT+"/documents/" + str(filexml.file_xml)
            filexml.save()
            f_id = filexml.id
            psaveXML(name_file, f_id, v_id)
            return HttpResponseRedirect('/collections/'+v_id+'/uploads')
    else:
        form = UploadFile()
    return render(request, 'scanhub/collection_upload.html',{'form':form})

def psaveXML(path, f_id, id_c):
    rep = NmapParser.parse_fromfile(path)
    for _host in rep.hosts:
        if _host.is_up():
            oh = Collection.objects.get(id=id_c)
            org = "No hostname"
            if _host.hostnames:
                org = get_tld("http://"+format("".join(_host.hostnames)))
            print org
            h = Host(owner_host=oh ,ip=_host.address, organization= org, hostname="".join(_host.hostnames), file_id=f_id)
            h.save()
            print(str(_host.hostnames))
            print("+ Host: {0} {1}".format(_host.address,
                                           " ".join(_host.hostnames)))
            # get CPE from service if available
            for s in _host.services:
                print("    Service: {0}/{1} ({2}) {3} {4}".format(s.port,
                                                          s.protocol,
                                                          s.state, s.service, s.banner))
                ho_p = Host.objects.get(id=h.id)
                po = Port(ip=ho_p,port=s.port,protocol=s.protocol,status=s.state,service=s.service,banner=s.banner)
                po.save()
                # NmapService.cpelist returns an array of CPE objects
                for _serv_cpe in s.cpelist:
                    print("        CPE: {0}".format(_serv_cpe.cpestring))
            if _host.os_fingerprinted:
                print("  OS Fingerprints")
                for osm in _host.os.osmatches:
                    if osm.accuracy > 94:
                        Host.objects.filter(id=h.id).update(so=format(osm.name))
                        print("    Found Match:{0} ({1}%)".format(osm.name,
                                                              osm.accuracy))
                    # NmapOSMatch.get_cpe() method return an array of string
                    # unlike NmapOSClass.cpelist which returns an array of CPE obj
                        for cpe in osm.get_cpe():
                            print("\t    CPE: {0}".format(cpe))
    

@login_required(login_url="/login/")
def collectionew(request):
    if request.POST:
        form = CollectionForm(request.POST)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.owner_id = request.user.id
            print collection
            collection.save()
            return HttpResponseRedirect('/collections')
    else:
        form = CollectionForm()
    return render(request, 'scanhub/collectionew.html', {'form':form})

@login_required(login_url="/login/")
def collection_view(request, b_id):
    if Collection.objects.filter(id=b_id, owner_id=request.user.id).exists():
        conn = connection.cursor()
        query_ports = "select sp.service, sp.port, count(sp.service) as topten from scans_host as sh, scans_port as sp where sh.owner_host_id="+b_id+" and sh.id=sp.ip_id group by sp.service,sp.port order by topten DESC limit 20"
        query_total_ports = "select count(sp.id) from scans_host as sh, scans_port as sp where sh.owner_host_id="+b_id+" and sh.id=sp.ip_id limit 1"
        conn.execute(query_ports)
        ports = conn.fetchall()
        conn.execute(query_total_ports)
        total_ports = conn.fetchone()
        tt = total_ports[0]
        conn.execute("select so, count(so) from scans_host where owner_host_id = "+b_id+" group by so;")
        top_os = conn.fetchall()
        conn.execute("select organization, count(organization) from scans_host where owner_host_id ="+b_id+"  group by organization;")
        top_org = conn.fetchall()
    return render(request, 'scanhub/view_collection.html',{'service':ports, 'total':tt, 'th':top_os, 'to':top_org, 'id_c' : b_id})


@login_required(login_url="/login/")
def search(request, x_id, search):
    if Collection.objects.filter(id=x_id, owner_id=request.user.id).exists():
        var = search.split(':')
        if "service" == var[0]:
            print var[1]
            
            return render(request, 'scanhub/search_collection.html', {})
        elif "host" == var[0]:
            print var[1]
            return render(request, 'scanhub/search_collection.html', {})
        elif "org" == var[0]:
            print var[1]
            return render(request, 'scanhub/search_collection.html', {})
    else:
        return render(request, 'scanhub/search_collection.html',{})


@login_required(login_url="/login/")
def logout(request):
    logout()
    return render(request, 'scanhub/login.html')
