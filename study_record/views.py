from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Q
from .models import Record, Day, Week
from .forms import RecordForm, DetailForm, FirstSettingsForm
from login.models import User
from .models import Record
from datetime import datetime, timedelta
from tzlocal import get_localzone
from pytz import timezone
import json


# change timedelta to string(ex. "1:40")
def td_to_s(x):
    h = int(x.seconds/60/60)
    m = str(int(x.seconds/60%60))
    if len(m) == 1:
        m = "0" + m
    h += 24 * x.days
    return str(h) + ":" + m


def m_to_s(x):
    h = str(int(x / 60))
    m = str(x % 60)
    if len(m) == 1:
        m += '0'
    return h+':'+m

def main(request):
    login = False
    if request.session.get("pk"):
        pk = request.session.get("pk")
        me = User.objects.get(pk=pk)
        login = True
        if me.name == "":
            return redirect("first_settings")
    today = datetime.today()
    tomorrow = datetime.strptime(today.strftime("%Y %m/%d") + " 00:00", "%Y %m/%d %H:%M") + timedelta(days=1)
    records = Record.objects.filter(end__gte=tomorrow-timedelta(days=7)).filter(start__lt=tomorrow)
    users = User.objects.exclude(name="").filter(ranking=True)
    dic = {}
    for user in users:
        dic[user.pk] = {"name":user.name, "yesterday":timedelta(seconds=0), "week":timedelta(seconds=0), "today":timedelta(seconds=0)}
    for record in records:
        s = (record.start + timedelta(hours=9)).replace(tzinfo=None)
        e = (record.end + timedelta(hours=9)).replace(tzinfo=None)
        if s < tomorrow - timedelta(days=7):
            dic[record.user]["week"] += e - tomorrow + timedelta(days=7)
        else:
            dic[record.user]["week"] += e - s
            if tomorrow - timedelta(days=1) < e:
                if tomorrow - timedelta(days=1) < s:
                    dic[record.user]["today"] += e - s
                else:
                    dic[record.user]["today"] += e - tomorrow + timedelta(days=1)
                    dic[record.user]["yesterday"] += tomorrow - timedelta(days=1) - s
            elif tomorrow - timedelta(days=2) < e:
                if tomorrow - timedelta(days=2) < s:
                    dic[record.user]["yesterday"] += e - s
                else:
                    dic[record.user]["yesterday"] += e - tomorrow + timedelta(days=2)
    ret = []
    for value in dic.values():
        ret.append({"name":value["name"], "yesterday":td_to_s(value["yesterday"]), "week":td_to_s(value["week"]), "today":td_to_s(value["today"])})
    if Day.objects.all().count() >= 3:
        days = Day.objects.order_by("-minutes")[:3]
    else:
        days = Day.objects.order_by("-minutes").all()
    ret_d = []
    for day in days:
        ret_d.append({"name":User.objects.get(pk=day.user).name, "length":m_to_s(day.minutes), "period":day.date.strftime("%Y/%m/%d")})
    while len(ret_d) < 3:
        ret_d.append({"name":None, "length":None, "period":None})
    weeks = get_weeks()
    ret_w = []
    for week in weeks:
        ret_w.append({"name":User.objects.get(pk=week.user).name, "length":m_to_s(week.minutes), "period":week.date.strftime("%Y/%m/%d")+'~'+(week.date+timedelta(days=6)).strftime("%m/%d")})
    while len(ret_w) < 3:
        ret_w.append({"name":None, "length":None, "period":None})
    return render(request, "study_record/main.html", {"dic":json.dumps(ret,ensure_ascii=False), "day":json.dumps(ret_d,ensure_ascii=False), "week":json.dumps(ret_w,ensure_ascii=False), "login":login})


def prepare_data_for_detail(start, user):
    end = start + timedelta(days=7)
    records = Record.objects.filter(user=user).filter(end__gte=start).filter(start__lt=end)
    dic = []
    e_to_j = {"Mon":"月", "Tue":"火", "Wed":"水", "Thu":"木", "Fri":"金", "Sat":"土", "Sun":"日"}
    for i in range(7):
        d = {"date":(start + timedelta(days=i)).strftime("%m/%d"), "day":e_to_j[(start + timedelta(days=i)).strftime("%a")], "record":[]}
        dic.append(d)
    for record in records:
        s = record.start + timedelta(hours=9)
        e = record.end + timedelta(hours=9)
        ja = get_localzone()
        if s.strftime("%m/%d") != e.strftime("%m/%d"):
            if s < timezone('UTC').localize(start.replace(tzinfo=None)):
                a = {
                    "name":record.subject,
                    "start":"0:00",
                    "length":td_to_s(e - timezone('UTC').localize(start.replace(tzinfo=None)))
                }
                dic[(ja.localize(datetime.strptime(e.strftime("%Y %m/%d")+" 00:00", "%Y %m/%d %H:%M"))-start).days]["record"].append(a)
                continue
            elif timezone('UTC').localize(end.replace(tzinfo=None)) <= e:
                a = {
                    "name":record.subject,
                    "start":s.strftime("%H:%M"),
                    "length":td_to_s(timezone('UTC').localize(end.replace(tzinfo=None)) - s)
                }
            else:
                a = {
                    "name":record.subject,
                    "start":s.strftime("%H:%M"),
                    "length":td_to_s(timezone('UTC').localize(datetime.strptime(s.strftime("%Y %m/%d")+" 00:00", "%Y %m/%d %H:%M") + timedelta(days=1)) - s)
                }
                b = {
                    "name":record.subject,
                    "start":"00:00",
                    "length":td_to_s(e - timezone('UTC').localize(datetime.strptime(e.strftime("%Y %m/%d")+" 00:00", "%Y %m/%d %H:%M")))
                }
                dic[(ja.localize(datetime.strptime(e.strftime("%Y %m/%d")+" 00:00", "%Y %m/%d %H:%M"))-start).days]["record"].append(b)
        else:
            a = {
                "name":record.subject,
                "start":s.strftime("%H:%M"),
                "length":td_to_s(e - s)
            }
        dic[(ja.localize(datetime.strptime(s.strftime("%Y %m/%d")+" 00:00", "%Y %m/%d %H:%M"))-start).days]["record"].append(a)
    return dic


def detail(request):
    if request.session.get("pk"):
        pk = request.session.get("pk")
        form = DetailForm(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                if 'date' in request.POST:
                    start = form.cleaned_data['start']
                    initial = start.strftime("%Y,%m,%d")
                    dic = prepare_data_for_detail(start, pk)
                    return render(request, "study_record/datafetch.test.html", {"dic":dic, "form":form, "initial":initial})
                # if 'backward' in request.POST:
                #     start = form.cleaned_data['start']
                #     start -= timedelta(days=7)
                #     initial = start.strftime("%Y,%m,%d")
                #     dic = prepare_data_for_detail(start, pk)
                #     return render(request, "study_record/datafetch.test.html", {"dic":dic, "form":form, "initial":initial})
                # if 'forward' in request.POST:
                #     start = form.cleaned_data['start']
                #     start += timedelta(days=7)
                #     initial = start.strftime("%Y,%m,%d")
                #     dic = prepare_data_for_detail(start, pk)
                #     return render(request, "study_record/datafetch.test.html", {"dic":dic, "form":form, "initial":initial})
        now = datetime.now()
        ja = get_localzone()
        start = ja.localize(datetime.strptime(now.strftime("%Y %m/%d") + " 00:00", "%Y %m/%d %H:%M") - timedelta(days=6))
        initial = start.strftime("%Y,%m,%d")
        dic = prepare_data_for_detail(start, pk)
        return render(request, "study_record/datafetch.test.html", {"dic":json.dumps(dic,ensure_ascii=False), "form":form, "initial":initial})
    else:
        return redirect("login")


def register_record(request):
    if request.session.get("pk"):
        pk = request.session.get("pk")
        form = RecordForm(request.POST or None)
        alert1 = alert2 = alert3 = False
        if request.method == 'POST':
            if form.is_valid():
                start = form.cleaned_data['start']
                end = form.cleaned_data['end']
                if start > end:
                    alert1 = True
                elif end - start >= timedelta(days=1):
                    alert2 = True
                if Record.objects.filter(pk=pk).filter(start__lt=start).filter(end__gt=start).exists():
                    alert3 = True
                elif Record.objects.filter(pk=pk).filter(start__lt=end).filter(end__gt=end).exists():
                    alert3 = True
                if alert1 or alert2 or alert3:
                    alerts = {"alert1":alert1, "alert2":alert2, "alert3":alert3}
                    return render(request, "study_record/register_record.html", {"form":form, "alerts":alerts})
                Record.objects.create(
                    user = pk,
                    start = form.cleaned_data['start'],
                    end = form.cleaned_data['end'],
                    subject = form.cleaned_data['subject'],
                )
                return redirect("main")
        alerts = {"alert1":alert1, "alert2":alert2, "alert3":alert3}
        return render(request, "study_record/register_record.html", {"form":form, "alerts":alerts})
    else:
        return redirect("login")


def first_settings(request):
    if request.session.get("pk"):
        pk = request.session.get("pk")
        initial = {'ranking':True}
        form = FirstSettingsForm(request.POST or None, initial=initial)
        if request.method == 'POST':
            if form.is_valid():
                me = User.objects.get(pk=pk)
                me.name = form.cleaned_data['name']
                me.ranking = form.cleaned_data['ranking']
                me.save()
                return redirect('main')
        return render(request, "study_record/first_settings.html", {"form":form})
    else:
        return redirect("login")


def edit_and_delete(request):
    if request.session.get("pk"):
        pk = request.session.get("pk")
        records = Record.objects.filter(user=pk).order_by("-start")
        form = RecordForm(request.POST or None)
        alert1 = alert2 = alert3 = alert4 = False
        if request.method == 'POST':
            if form.is_valid():
                if "register" in request.POST:
                    subject = form.cleaned_data['subject']
                    start = form.cleaned_data['start']
                    end = form.cleaned_data['end']
                    if start > end:
                        alert1 = True
                    elif end - start >= timedelta(days=1):
                        alert2 = True
                    if Record.objects.filter(user=pk).exclude(end__lte=start).exclude(start__gte=end).exists():
                        alert3 = True
                    if subject == "":
                        alert4 = True
                    if alert1 or alert2 or alert3 or alert4:
                        ret = []
                        for record in records:
                            s = record.start + timedelta(hours=9)
                            e = record.end + timedelta(hours=9)
                            ret.append({'pk':record.pk, 'start':s.strftime("%m/%d %H:%M"), 'end':e.strftime("%m/%d %H:%M"), 'subject':record.subject})
                        alerts = {"alert1":alert1, "alert2":alert2, "alert3":alert3, "alert4":alert4}
                        return render(request, "study_record/edit_and_delete.html", {"records":ret, "form":form, "alerts":alerts})
                    start = form.cleaned_data['start']
                    end = form.cleaned_data['end']
                    Record.objects.create(
                        user = pk,
                        start = start,
                        end = end,
                        subject = form.cleaned_data['subject'],
                    )
                    update_d_w(pk, start, end, 1)
                for record in records:
                    if 'edit'+str(record.pk) in request.POST:
                        return redirect('edit', record.pk)
                    elif 'delete'+str(record.pk) in request.POST:
                        return redirect('delete', record.pk)
        ret = []
        for record in records:
            s = record.start + timedelta(hours=9)
            e = record.end + timedelta(hours=9)
            ret.append({'pk':record.pk, 'start':s.strftime("%m/%d %H:%M"), 'end':e.strftime("%m/%d %H:%M"), 'subject':record.subject})
        alerts = {"alert1":alert1, "alert2":alert2, "alert3":alert3, "alert4":alert4}
        return render(request, "study_record/edit_and_delete.html", {"records":ret, "form":form, "alerts":alerts})
    else:
        return redirect("login")


def edit(request, record_pk):
    if request.session.get("pk"):
        pk = request.session.get("pk")
        record = Record.objects.get(pk=record_pk)
        s = record.start + timedelta(hours=9)
        e = record.end + timedelta(hours=9)
        initial_s = s.strftime("%Y,%m,%d,%H,%M")
        initial_e = e.strftime("%Y,%m,%d,%H,%M")
        alert1 = alert2 = alert3 = False
        if record.user == pk:
            initial = {'subject':record.subject}
            form = RecordForm(request.POST or None, initial=initial)
            if request.method == 'POST':
                if 'save' in request.POST:
                    if form.is_valid():
                        start = form.cleaned_data['start']
                        end = form.cleaned_data['end']
                        if start > end:
                            alert1 = True
                        elif end - start >= timedelta(days=1):
                            alert2 = True
                        if Record.objects.filter(pk=pk).filter(start__lt=start).filter(end__gt=start).exists():
                            alert3 = True
                        elif Record.objects.filter(pk=pk).filter(start__lt=end).filter(end__gt=end).exists():
                            alert3 = True
                        if alert1 or alert2 or alert3:
                            alerts = {"alert1":alert1, "alert2":alert2, "alert3":alert3}
                            return render(request, "study_record/edit.html", {"form":form, "initials":{"s":initial_s, "e":initial_e}, "alerts":alerts})
                        update_d_w(pk, record.start, record.end, -1)
                        record.subject = form.cleaned_data['subject']
                        record.start = form.cleaned_data['start']
                        record.end = form.cleaned_data['end']
                        record.save()
                        update_d_w(pk, record.start, record.end, 1)
                        return redirect("edit_and_delete")
                if 'reset' in request.POST:
                    return redirect("edit", record_pk)
            initial = {'subject':record.subject}
            form = RecordForm(request.POST or None, initial=initial)
            alerts = {"alert1":alert1, "alert2":alert2, "alert3":alert3}
            return render(request, "study_record/edit.html", {"form":form, "initials":{"s":initial_s, "e":initial_e}, "alerts":alerts})
        else:
            return redirect("not_allowed")
    else:
        return redirect("login")


def delete(request, record_pk):
    if request.session.get("pk"):
        pk = request.session.get("pk")
        record = Record.objects.get(pk=record_pk)
        if record.user == pk:
            if request.method == 'POST':
                if 'yes' in request.POST:
                    update_d_w(pk, record.start, record.end, -1)
                    record.delete()
                return redirect("edit_and_delete")
            s = record.start + timedelta(hours=9)
            e = record.end + timedelta(hours=9)
            s = s.strftime("%m月%d日　%H：%M")
            e = e.strftime("%m月%d日　%H：%M")
            ret = {"subject":record.subject, "start":s, "end":e}
            return render(request, "study_record/delete.html", {"record":ret})
        else:
            return redirect("not_allowed")
    else:
        return redirect("login")


def not_allowed(request):
    return render(request, "study_record/not_allowed.html")


def update_d_w(pk, start, end, pos_neg):
    ja = get_localzone()
    if start.tzinfo == timezone('UTC'):
        start = start.astimezone(ja)
    if end.tzinfo == timezone('UTC'):
        end = end.astimezone(ja)
    if start.strftime("%Y %m/%d") == end.strftime("%Y %m/%d"):
        day = Day.objects.get_or_create(user=pk, date=start.date())
        day[0].minutes += int((end - start).seconds / 60) * pos_neg
        day[0].save()
        for i in range(7):
            week = Week.objects.get_or_create(user=pk, date=start.date()-timedelta(days=i))
            week[0].minutes += int((end - start).seconds / 60) * pos_neg
            week[0].save()
    else:
        day1 = Day.objects.get_or_create(user=pk, date=start.date())
        day2 = Day.objects.get_or_create(user=pk, date=end.date())
        dt = datetime.strptime(end.strftime("%Y %m/%d") + " 00:00", "%Y %m/%d %H:%M")
        dt = ja.localize(dt)
        day1[0].minutes += int((dt - start).seconds / 60) * pos_neg
        day2[0].minutes += int((end - dt).seconds / 60) * pos_neg
        day1[0].save()
        day2[0].save()
        for i in range(7):
            week1 = Week.objects.get_or_create(user=pk, date=start.date()-timedelta(days=i))
            week2 = Week.objects.get_or_create(user=pk, date=start.date()-timedelta(days=i-1))
            week1[0].minutes += int((dt - start).seconds / 60) * pos_neg
            week2[0].minutes += int((end - dt).seconds / 60) * pos_neg
            week1[0].save()
            week2[0].save()
    return


def get_weeks():
    ret = []
    if Week.objects.exists():
        weeks = Week.objects.order_by("-minutes").all()
        for i in range(3):
            if weeks.count() == 0:
                break
            ret.append(weeks.first())
            temp = weeks.first()
            # 異なるpkまたは一週間以上ずれているもの
            weeks = weeks.filter(Q(user__gt=temp.user) | Q(user__lt=temp.user) | Q(date__gte=temp.date+timedelta(days=7)) | Q(date__lte=temp.date-timedelta(days=7)))
    return ret
