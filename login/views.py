from django.shortcuts import render, redirect
from django.views import View
from .models import User, IdCounter
from .forms import LoginForm, RegisterMailForm, ResetForm, ResetMailForm, RegisterForm
from django.core.mail import send_mail


def login(request):
    alert1 = False
    alert2 = False
    alert3 = False
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            mail = form.cleaned_data['email']
            if User.objects.filter(email=mail).exists():
                pw = form.cleaned_data['password']
                if User.objects.filter(email=mail).filter(password=pw).exists():
                    users = User.objects.filter(email=mail).filter(password=pw)
                    if len(users) == 1:
                        user = User.objects.filter(email=mail).get(password=pw)
                        request.session['pk'] = user.pk
                        return redirect('main')
                    else:
                        alert3 = True
                else:
                    alert2 = True
            else:
                alert1 = True
            alerts = {'alert1':alert1, 'alert2':alert2, 'alert3':alert3}
            return render(request, 'login/login.html', {'form':form, 'alerts':alerts})
    alerts = {'alert1':alert1, 'alert2':alert2, 'alert3':alert3}
    return render(request, 'login/login.html', {'form':form, 'alerts':alerts})


def register_mail(request):
    form = RegisterMailForm(request.POST or None)
    alert1 = False
    alert2 = False
    alert3 = False
    if request.method == 'POST':
        if form.is_valid():
            if form.cleaned_data['password1'] != form.cleaned_data['password2']:
                alert1 = True
            email = form.cleaned_data['email']
            if User.objects.filter(activated=True).filter(email=email).exists():
                alert2 = True
            if len(form.cleaned_data['password1']) < 4 or len(form.cleaned_data['password2']) < 4:
                alert3 = True
            if alert1 or alert2 or alert3:
                alerts = {'alert1':alert1, 'alert2':alert2, 'alert3':alert3}
                return render(request, 'login/register_mail.html', {'form': form, 'alerts':alerts})
            else:
                user = User(
                    email = form.cleaned_data['email'],
                    password = form.cleaned_data['password1'],
                )
                user.save()
                subject = "本登録"
                message1 = "以下のURLから本登録を行なってください。\n"
                link = "{0}://{1}".format(request.scheme, request.get_host()) + '/register/'
                link += str(user.pk)
                message2 = "\nこのアカウントのパスワードは {} です。".format(user.password)
                from_email = 'calendar.tarou@gmail.com'
                recipient_list = []
                recipient_list.append(form.cleaned_data['email'])
                send_mail(subject, message1+link+message2, from_email, recipient_list)
                return redirect('sent_a_mail')
    alerts = {'alert1':alert1, 'alert2':alert2, 'alert3':alert3}
    return render(request, 'login/register_mail.html', {'form': form, 'alerts':alerts})


def sent_a_mail(request):
    return render(request, 'login/sent_a_mail.html')


def reset_mail(request):
    form = ResetMailForm(request.POST or None)
    alert = False
    if request.method == 'POST':
        if form.is_valid():
            users = User.objects.filter(email=form.cleaned_data['email'])
            alert = True
            for user in users:
                if user.activated:
                    alert = False
            if alert:
                return render(request, 'login/reset_mail.html', {'form':form, 'alert':alert})
            else:
                user = User.objects.get(email=form.cleaned_data['email'])
                subject = "パワードの変更"
                message = "パスワードの再設定は以下のURLから行うことができます。\n"
                link = "{0}://{1}".format(request.scheme, request.get_host()) + '/reset/'
                link += str(user.pk)
                from_email = 'calendar.tarou@gmail.com'
                recipient_list = []
                recipient_list.append(form.cleaned_data['email'])
                send_mail(subject, message+link, from_email, recipient_list)
                return redirect('sent_a_mail')
    return render(request, 'login/reset_mail.html', {'form':form, 'alert':alert})


def reset(request, pk):
    form = ResetForm(request.POST or None)
    alert1 = False
    alert2 = False
    if request.method == 'POST':
        if form.is_valid():
            if len(form.cleaned_data['password1']) < 4 or len(form.cleaned_data['password2']) < 4:
                alert1 = True
            user = User.objects.get(pk=pk)
            if form.cleaned_data['email'] != user.email:
                alert2 = True
            if alert1 or alert2:
                return render(request, 'login/reset.html', {'form':form, 'alert1':alert1, 'alert2':alert2})
            else:
                user.password = form.cleaned_data['password1']
                user.save()
                request.session['pk'] = pk
                return redirect('reset_completed')
    return render(request, 'login/reset.html', {'form':form, 'alert1':alert1, 'alert2':alert2})


def reset_completed(request):
    if request.method == 'POST':
        return redirect('main')
    return render(request, 'login/reset_completed.html')


def register(request, pk):
    form = RegisterForm(request.POST or None)
    alert1 = False
    alert2 = False
    if User.objects.filter(pk=pk).exists():
        user = User.objects.get(pk=pk)
        if user.activated:
            return redirect('already_registered')
        else:
            if request.method == 'POST':
                if form.is_valid():
                    pw = form.cleaned_data['password']
                    if len(pw) < 4:
                        alert1 = True
                    if user.password != form.cleaned_data['password']:
                        alert2 = True
                    if not alert1 and not alert2:
                        if not IdCounter.objects.exists():
                            IdCounter.objects.create()
                        ID = IdCounter.objects.get()
                        user = User.objects.get(pk=pk)
                        user.activated = True
                        user.userid = create_ID(str(ID.counter))
                        user.save()
                        ID.counter += 1
                        ID.save()
                        users = User.objects.filter(email=user.email).exclude(pk=pk)
                        for u in users:
                            u.delete()
                        request.session['pk'] = user.pk
                        return redirect('register_completed')
    else:
        return redirect()
    return render(request, 'login/register.html', {'form':form, 'alert1':alert1, 'alert2':alert2})


def register_completed(request):
    if request.method == 'POST':
        return redirect('main')
    return render(request, 'login/register_completed.html')


def create_ID(n_str):
    while len(n_str) < 9:
        n_str = '0' + n_str
    return n_str


def logout(request):
    if "pk" in request.session.keys():
        del request.session["pk"]
    return redirect("main")


def already_registered(request):
    if request.method == 'POST':
        return redirect("login")
    return render(request, 'login/already_registered.html')


def already_used(request):
    if request.method == 'POST':
        return redirect("login")
    return render(request, 'login/already_used.html')
