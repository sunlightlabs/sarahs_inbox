from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.paginator import Paginator
from urllib import unquote
from mail.models import *

def _annotate_threads(request, threads):
    read_cookie = unquote(request.COOKIES.get('kagan_read','')).replace(',,', ',')
    if len(read_cookie)>0:
        if read_cookie[0]==',':
            read_cookie = read_cookie[1:]
        if read_cookie[-1]==',':
            read_cookie = read_cookie[:-1]

    try:
        read_ids = map(lambda x: (x!='') and int(x) or 0, read_cookie.split(','))
    except:
        read_ids = []

    threads_obj = []
    for thread in threads:
        threads_obj.append({'read': (thread.id in read_ids), 'obj': thread})
    return threads_obj

def index(request):    
    threads = Thread.objects.all().order_by('-date')

    p = Paginator(threads, 50)
    page_num = 1
    try:
        page_num = int(request.GET.get('page', 1))
    except:
        pass
    page = p.page(page_num)
    threads = []
    for thread in page.object_list:
        threads.append(thread)
    threads = _annotate_threads(request,threads)
    
    return render_to_response('index.html', {'range': "<strong>%d</strong> - <strong>%d</strong> of <strong>%d</strong>" % (page.start_index(), page.end_index(), Thread.objects.all().count()), 'num_pages': p.num_pages, 'next': page_num<p.num_pages and min(p.num_pages,page_num+1) or False, 'prev': page_num>1 and max(1, page_num-1) or False, 'first': '1', 'last': p.num_pages, 'current_page': page_num, 'threads': threads}, context_instance=RequestContext(request))

def thread(request, thread_id):
    try:
        thread = Thread.objects.get(id=thread_id)
    except Thread.DoesNotExist, e:
        return HttpResponseRedirect(reverse('mail.views.index'))
    
    emails = Email.objects.filter(email_thread=thread).order_by('creation_date_time')
    
    return render_to_response('thread.html', {'thread': thread, 'emails': emails }, context_instance=RequestContext(request))