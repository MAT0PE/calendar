from django.shortcuts import render, redirect
from login.models import User
from study_record.models import Record
from .models import Message, Request
from .forms import ChatForm, ProfileForm
from datetime import datetime
from pytz import timezone
from django.contrib import messages
from django.db.models import Q


def friends(request):
    if request.session.get("pk"):
        pk = request.session.get("pk")
        me = User.objects.get(pk=pk)
        friends = User.objects.filter(pk__in=str_to_arr(me.friends))
        if request.method == 'POST':
            for friend in friends:
                if str(friend.pk) in request.POST:
                    return redirect('chat', you=friend.userid)
        ret = []
        for friend in friends:
            messages = Message.objects.filter(sender__in=[me.pk, friend.pk]).filter(receiver__in=[me.pk, friend.pk]).order_by('time')
            last_message = messages.last()
            unread = 0
            for message in messages[::-1]:
                if message.receiver == pk:
                    if message.read:
                        break
                    else:
                        unread += 1
            if last_message == None:
                d = {'pk':friend.pk, 'name':friend.name, 'last_text':'', 'last_time':timezone('UTC').localize(datetime(2020, 1, 1, 0, 0)), 'unread':unread}
            else:
                d = {'pk':friend.pk, 'name':friend.name, 'last_text':last_message.text, 'last_time':last_message.time, 'unread':unread}
            ret.append(d)
        ret = sorted(ret, key=lambda x: x['last_time'], reverse=True)
        return render(request, "friends/friends.html", {'friends':ret})
    else:
        return redirect("login")


def chat(request, you):
    if request.session.get("pk"):
        me = request.session.get("pk")
        initial_dict = {
            'text':""
        }
        you = User.objects.get(userid=you)
        form = ChatForm(request.POST or None, initial=initial_dict)
        if request.method == 'POST':
            if form.is_valid():
                Message.objects.create(
                    sender = me,
                    receiver = you.pk,
                    time = datetime.now(),
                    text = form.cleaned_data['text'],
                    read = False,
                )
                return redirect("chat", you.userid)
        messages = Message.objects.filter(sender__in=[me, you.pk]).filter(receiver__in=[me, you.pk]).order_by('time')
        ret = []
        for message in messages:
            if message.sender == me:
                d = {'text':message.text, 'me_to_you':True}
            else:
                d = {'text':message.text, 'me_to_you':False}
            ret.append(d)
        for message in messages[::-1]:
            if message.receiver == me:
                if message.read:
                    break
                else:
                    message.read = True
                    message.save()
        return render(request, "friends/chat.html", {'messages':ret, 'name':you.name, 'form':form})
    else:
        return redirect("login")


# change string to array (useful when converting User.friends)
def str_to_arr(s):
    ret = []
    if s != '':
        t = ""
        for c in s:
            if c == ',':
                ret.append(int(t))
                t = ""
            else:
                t += c
        ret.append(int(t))
    return ret


def search(request):
    if request.session.get("pk"):
        pk = request.session.get("pk")
        dicts = []
        me = User.objects.get(pk=pk)
        users = User.objects.filter(activated=True).exclude(pk=pk)
        text = ""
        keyword = request.GET.get('keyword')
        if keyword:
            users = users.filter(
                    Q(name__icontains=keyword) | Q(userid__icontains=keyword)
                )
            for user in users:
                if Request.objects.filter(sender=pk).filter(receiver=user.pk).exists():
                    dicts.append({'name':user.name, 'userid':user.userid, 'message':user.message, 'state':1})
                elif user.pk in str_to_arr(me.friends):
                    dicts.append({'name':user.name, 'userid':user.userid, 'message':user.message, 'state':2})
                else:
                    dicts.append({'name':user.name, 'userid':user.userid, 'message':user.message, 'state':3})
            text = '「{}」の検索結果'.format(keyword)
        if request.method == 'POST':
            for user in users:
                if str(user.userid) in request.POST:
                    Request.objects.create(
                        sender = pk,
                        receiver = user.pk,
                    )
                    dicts = []
                    users = User.objects.filter(activated=True).exclude(pk=pk)
                    users = users.filter(
                        Q(name__icontains=keyword) | Q(userid__icontains=keyword)
                    )
                    for user in users:
                        if Request.objects.filter(sender=pk).filter(receiver=user.pk).exists():
                            dicts.append({'name':user.name, 'userid':user.userid, 'message':user.message, 'state':1})
                        elif user.pk in str_to_arr(me.friends):
                            dicts.append({'name':user.name, 'userid':user.userid, 'message':user.message, 'state':2})
                        else:
                            dicts.append({'name':user.name, 'userid':user.userid, 'message':user.message, 'state':3})
                    return render(request, 'friends/search.html', {'users':dicts, 'text':text})
        return render(request, 'friends/search.html', {'users':dicts, 'text':text})
    else:
        return redirect("login")


def requests(request):
    if request.session.get("pk"):
        pk = request.session.get("pk")
        requests = Request.objects.filter(receiver=pk)
        if request.method == 'POST':
            for r in requests:
                if 'approve'+str(r.pk) in request.POST:
                    me = User.objects.get(pk=pk)
                    if me.friends == "":
                        me.friends = str(r.sender)
                    else:
                        me.friends += ','+str(r.sender)
                    me.save()
                    you = User.objects.get(pk=r.sender)
                    if you.friends == "":
                        you.friends = str(pk)
                    else:
                        you.friends += ','+str(pk)
                    you.save()
                    r.delete()
                    requests = Request.objects.filter(receiver=pk)
                    dicts = []
                    for r in requests:
                        user = User.objects.get(pk=r.sender)
                        dicts.append({'name':user.name, 'userid':user.userid, 'message':user.message, 'pk':r.pk})
                    return render(request, 'friends/requests.html', {'requests':dicts})
                if 'deny'+str(r.pk) in request.POST:
                    r.delete()
                    requests = Request.objects.filter(receiver=pk)
                    dicts = []
                    for r in requests:
                        user = User.objects.get(pk=r.sender)
                        dicts.append({'name':user.name, 'userid':user.userid, 'message':user.message, 'pk':r.pk})
                    return render(request, 'friends/requests.html', {'requests':dicts})
        dicts = []
        for r in requests:
            user = User.objects.get(pk=r.sender)
            dicts.append({'name':user.name, 'userid':user.userid, 'message':user.message, 'pk':r.pk})
        return render(request, 'friends/requests.html', {'requests':dicts})
    else:
        return redirect("login")


def profile(request):
    if request.session.get("pk"):
        pk = request.session.get("pk")
        user = User.objects.get(pk=pk)
        if request.method == 'POST':
            return redirect('edit_profile')
        return render(request, 'friends/profile.html', {'name':user.name, 'id':user.userid, 'message':user.message, 'ranking':user.ranking})
    else:
        return redirect("login")


def edit_profile(request):
    if request.session.get("pk"):
        pk = request.session.get("pk")
        user = User.objects.get(pk=pk)
        initial_dict = {'name':user.name, 'message':user.message, 'ranking':user.ranking}
        form = ProfileForm(request.POST or None, initial=initial_dict)
        if request.method == 'POST':
            if form.is_valid():
                user.name = form.cleaned_data['name']
                user.message = form.cleaned_data['message']
                user.ranking = form.cleaned_data['ranking']
                user.save()
                return redirect('my_profile')
        return render(request, 'friends/edit_profile.html', {'form':form})
    else:
        return redirect("login")


def create_ID(n_str):
    while len(n_str) < 9:
        n_str = '0' + n_str
    return n_str


def your_profile(request, id):
    pk = -1
    if request.session.get("pk"):
        pk = request.session.get("pk")
        me = User.objects.get(pk=pk)
        you = User.objects.get(userid=id)
        initial_dict = {'name':user.name, 'message':user.message, 'ranking':user.ranking}
        form = ProfileForm(request.POST or None, initial=initial_dict)
        if request.method == 'POST':
            if form.is_valid():
                user.name = form.cleaned_data['name']
                user.message = form.cleaned_data['message']
                user.ranking = form.cleaned_data['ranking']
                user.save()
                return redirect('my_profile')
        return render(request, 'friends/edit_profile.html', {'form':form})
    else:
        return redirect("login")
