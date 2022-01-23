from django.shortcuts import render, redirect
from .models import Vocabulary
from datetime import date, timedelta
from .forms import PostForm, OneByOne, Json
import json


def type_in_foreign(request):
    if request.session.get("pk"):
        pk = request.session.get("pk")
        today = date.today()
        vocabs = Vocabulary.objects.filter(user=pk).filter(date__lte=today).order_by('date')
        ls = "["
        for vocab in vocabs:
            ls += '{\"foreign\":\"' + vocab.foreign + '\",'
            ls += '\"japanese\":\"' + vocab.japanese + '\",'
            ls += '\"sentence\":\"' + vocab.sentence + '\",'
            ls += '\"state\":' + str(vocab.state) + ','
            ls += '\"pk\":' + str(vocab.pk) + '},'
        if len(ls) != 1:
            ls = ls[:-1] + "]"
        else:
            ls += "]"
        form = PostForm(request.POST or None)
        if request.method == "POST":
            if form.is_valid():
                data_str = form.cleaned_data['data']
                dicts = json.loads(data_str)
                for d in dicts:
                    if 'done' in d.keys():
                        vocab = Vocabulary.objects.get(pk=d['pk'])
                        vocab.state = d['state']
                        vocab.date = today + timedelta(days=2**d['state'])
                        vocab.save()
                return redirect("vocabulary")
        return render(request, 'anki/francaisjaponais.html', {'form':form, 'vocabs':ls})
    else:
        return redirect("login")


def check_answer(request):
    if request.session.get("pk"):
        pk = request.session.get("pk")
        today = date.today()
        vocabs = Vocabulary.objects.filter(user=pk).filter(date__lte=today).order_by('date')
        ls = "["
        for vocab in vocabs:
            ls += '{\"foreign\":\"' + vocab.foreign + '\",'
            ls += '\"japanese\":\"' + vocab.japanese + '\",'
            ls += '\"sentence\":\"' + vocab.sentence + '\",'
            ls += '\"state\":' + str(vocab.state) + ','
            ls += '\"pk\":' + str(vocab.pk) + '},'
        if len(ls) != 1:
            ls = ls[:-1] + "]"
        else:
            ls += "]"
        form = PostForm(request.POST or None)
        if request.method == "POST":
            if form.is_valid():
                data_str = form.cleaned_data['data']
                dicts = json.loads(data_str)
                for d in dicts:
                    if 'done' in d.keys():
                        vocab = Vocabulary.objects.get(pk=d['pk'])
                        vocab.state = d['state']
                        vocab.date = today + timedelta(days=2**d['state'])
                        vocab.save()
                return redirect("vocabulary")
        return render(request, 'anki/japonaisfrancais.html', {'form':form, 'vocabs':ls})
    else:
        return redirect("login")


def vocabulary(request):
    if request.session.get("pk"):
        pk = request.session.get("pk")
        exist = False
        message = []
        num = 0
        today = date.today()
        vocabs = Vocabulary.objects.filter(user=pk).filter(date__lte=today).order_by('date')
        ls = "["
        for vocab in vocabs:
            ls += '{\"foreign\":\"' + vocab.foreign + '\",'
            ls += '\"japanese\":\"' + vocab.japanese + '\",'
            ls += '\"sentence\":\"' + vocab.sentence + '\",'
            ls += '\"state\":' + str(vocab.state) + ','
            ls += '\"pk\":' + str(vocab.pk) + '},'
        if len(ls) != 1:
            ls = ls[:-1] + "]"
        else:
            ls += "]"
        if Vocabulary.objects.filter(user=pk).exists():
            exist = True
            vocabs = Vocabulary.objects.filter(user=pk).order_by('state')
            state = vocabs[0].state
            count = 0
            for vocab in vocabs:
                if state == vocab.state:
                    count += 1
                else:
                    message.append({'state':state, 'num':count})
                    count = 1
                    state = vocab.state
            message.append({'state':state, 'num':count})
            today = date.today()
            remain = Vocabulary.objects.filter(user=pk).filter(date__lte=today)
            num = len(remain)
        form = PostForm(request.POST or None)
        if request.method == "POST":
            if form.is_valid():
                data_str = form.cleaned_data['data']
                dicts = json.loads(data_str)
                for d in dicts:
                    if 'done' in d.keys():
                        vocab = Vocabulary.objects.get(pk=d['pk'])
                        vocab.state = d['state']
                        vocab.date = today + timedelta(days=2**d['state'])
                        vocab.save()
                return redirect("vocabulary")
        return render(request, 'anki/vocabulary.html', {'exist':exist, 'message':message, 'remain':num, 'form':form, 'vocabs':ls})
    else:
        return redirect("login")


def register_vocab(request):
    if request.session.get("pk"):
        one_by_one = OneByOne(request.POST or None)
        json_form = Json(request.POST or None)
        alert1 = False
        alert2 = False
        pk = request.session.get("pk")
        tomorrow = date.today() + timedelta(days=1)
        if request.method == "POST":
            if "obo" in request.POST:
                if one_by_one.is_valid():
                    if ('"' not in one_by_one.cleaned_data['foreign']) and ('"' not in one_by_one.cleaned_data['japanese']) and ('"' not in one_by_one.cleaned_data['sentence']):
                        d = {'foreign':one_by_one.cleaned_data['foreign'], 'japanese':one_by_one.cleaned_data['japanese']}
                        if one_by_one.cleaned_data['sentence'] != '':
                            d['sentence'] = one_by_one.cleaned_data['sentence']
                            d['exist'] = True
                        else:
                            d['exist'] = False
                        jn = [d]
                        for j in jn:
                            vocab = Vocabulary.objects.create(
                                foreign = j['foreign'],
                                japanese = j['japanese'],
                                date = tomorrow,
                                state = 0,
                                user = pk,
                            )
                            if 'sentence' in j.keys():
                                    vocab.sentence = j['sentence']
                            vocab.save()
                        request.session['jn'] = jn
                        return redirect("verification")
                    else:
                        alert1 = True
                        return render(request, 'anki/register_vocab.html', {'one_by_one':one_by_one, 'json':json_form, 'alert1':alert1, 'alert2':alert2})
            if "j" in request.POST:
                if json_form.is_valid():
                    jn = json_form.cleaned_data['json'] 
                    if is_json(jn):
                        jn = json.loads(jn)
                        for j in jn:
                            vocab = Vocabulary.objects.create(
                                foreign = j['foreign'],
                                japanese = j['japanese'],
                                date = tomorrow,
                                state = 0,
                                user = pk,
                            )
                            j['exist'] = False
                            if 'sentence' in j.keys():
                                    vocab.sentence = j['sentence']
                                    j['exist'] = True
                            vocab.save()
                        request.session['jn'] = jn
                        return redirect("verification")
                    else:
                        alert2 = True
                        return render(request, 'anki/register_vocab.html', {'one_by_one':one_by_one, 'json':json_form, 'alert1':alert1, 'alert2':alert2})
        return render(request, 'anki/register_vocab.html', {'one_by_one':one_by_one, 'json':json_form, 'alert1':alert1, 'alert2':alert2})
    else:
        return redirect("login")


def verification(request):
    if request.session.get("pk"):
        if request.session.get("jn"):
            pk = request.session.get("pk")
            jn = request.session.get("jn")
            return render(request, 'anki/verification.html', {'jn':jn})
        else:
            return redirect('register_vocab')
    else:
        return redirect("login")


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True