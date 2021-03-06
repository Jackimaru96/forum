from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.contrib.auth import authenticate
from pyp.models import Faculty, Module, ModuleYear, Answer, AnswerFile, Comments
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from .forms import UploadFileForm, Commentform


def homepage(request):
    return HttpResponse('index')


def index(request):
    if request.method=="POST":
        try:
            module = Module.objects.get(module_code=request.POST['code'].upper())
        except ObjectDoesNotExist:
            return render(request,'pyp/index.html',{'error_message':'Module code can\'t be found'})
        else:
            if module:
                faculty= module.faculty
                return HttpResponseRedirect(reverse('pyp:viewYear', args=(faculty.faculty_code,module.module_code,)))
    return render(request, 'pyp/index.html')


def timeline(request):
    return render(request, 'pyp/timeline.html')


def modules(request, faculty_code):
    template = loader.get_template('pyp/modules.html')
    faculty = get_object_or_404(Faculty, faculty_code=faculty_code)
    return render(request, 'pyp/modules.html', {'faculty': faculty})



def viewYear(request, faculty_code, module_code):
    module = get_object_or_404(Module, module_code=module_code)
    faculty = get_object_or_404(Faculty, faculty_code=faculty_code)
    if not module.faculty.faculty_code == faculty_code:
        raise Http404("WTF are u doing")
    return render(request, 'pyp/year.html', {'module': module, 'faculty': faculty})


def viewAnswer(request, faculty_code, module_code, year_id):
    faculty = get_object_or_404(Faculty, faculty_code=faculty_code)
    module = get_object_or_404(Module, module_code=module_code)
    year = get_object_or_404(ModuleYear, pk=year_id)

    if request.method == 'POST':
        if 'upvote' in request.POST:
            answer = get_object_or_404(Answer, pk=request.POST['upvote'])
            answer.upvote += 1
            answer.save()
        elif 'downvote' in request.POST:
            answer = get_object_or_404(Answer, pk=request.POST['downvote'])
            answer.downvote += 1
            answer.save()
        elif 'delete' in request.POST:
            answer = get_object_or_404(Answer, pk=request.POST['delete'])
            answer.delete()
        else:
            answer = Answer(answer_text="test", author=request.user)
            year.answer_set.add(answer, bulk=False)
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                # file is saved
                answerf = form.save(commit=False)
                answer.answerfile_set.add(answerf, bulk=False)
                answerf.save()
        return HttpResponseRedirect(request.path_info)
    form = UploadFileForm()
    return render(request, 'pyp/answers.html', {'form': form, 'module': module, 'year': year, 'faculty': faculty})


def downloadAnswer(request, faculty_code, module_id, year_id, answerf_id):
    fileanswer = get_object_or_404(AnswerFile, pk=answerf_id)
    response = HttpResponse(open(str(fileanswer.file), 'rb').read())
    response['Content-Type'] = 'plain'
    response['Content-Disposition'] = fileanswer.title

    return response


def viewComment(request, faculty_code, module_code, year_id, answer_id):
    faculty = get_object_or_404(Faculty, faculty_code=faculty_code)
    module = get_object_or_404(Module, module_code=module_code)
    year = get_object_or_404(ModuleYear, pk=year_id)
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.method == 'POST':
        if request.user.is_authenticated:
            username = request.user.id
        else:
            username = 'annoyamous'
        answer.comments_set.create(user=username, text=request.POST['comment'], pub_date=timezone.now())

        return HttpResponseRedirect(request.path_info)
    else:
        form = Commentform()
    return render(request, 'pyp/comments.html',
                  {'form': form, 'module': module, 'year': year, 'faculty': faculty, 'answer': answer})


