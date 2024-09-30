from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Quiz, Question, Answer, Marks_Of_User
from .forms import QuizForm, QuestionForm
from django.forms import inlineformset_factory

def index(request):
    quiz = Quiz.objects.all()
    return render(request, "index.html", {'quiz': quiz})

@login_required(login_url='/login')
def quiz(request, myid):
    quiz = get_object_or_404(Quiz, id=myid)
    return render(request, "quiz.html", {'quiz': quiz})

def quiz_data_view(request, myid):
    quiz = get_object_or_404(Quiz, id=myid)
    questions = [{str(q): [a.content for a in q.get_answers()]} for q in quiz.get_questions()]
    return JsonResponse({'data': questions, 'time': quiz.time})
    
def save_quiz_view(request, myid):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        user = request.user
        quiz = get_object_or_404(Quiz, id=myid)
        score = 0
        marks = []

        for question in quiz.get_questions():
            selected_answer = request.POST.get(question.content)
            correct_answer = question.get_answers().filter(correct=True).first()

            if selected_answer:
                is_correct = selected_answer == correct_answer.content if correct_answer else False
                if is_correct:
                    score += 1
                marks.append({
                    str(question): {
                        'correct_answer': correct_answer.content if correct_answer else None,
                        'answered': selected_answer,
                        'is_correct': is_correct,
                    }
                })
            else:
                marks.append({str(question): 'not answered'})

        Marks_Of_User.objects.create(quiz=quiz, user=user, score=score)
        return JsonResponse({'passed': True, 'score': score, 'marks': marks})

    return JsonResponse({'passed': False, 'error': 'Invalid request'}, status=400)

def Signup(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password = request.POST['password1']
        confirm_password = request.POST['password2']
        
        if password != confirm_password:
            return render(request, "signup.html", {'error': "Passwords do not match."})
        
        user = User.objects.create_user(username, email, password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        return render(request, 'login.html')  

    return render(request, "signup.html")

def Login(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username=username, password=password)
        
        if user:
            login(request, user)
            return redirect("/")
        else:
            return render(request, "login.html", {'error': "Invalid credentials."}) 
    return render(request, "login.html")

def Logout(request):
    logout(request)
    return redirect('/')

def add_quiz(request):
    if request.method == "POST":
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save()
            return render(request, "add_quiz.html", {'obj': quiz})
    else:
        form = QuizForm()
    return render(request, "add_quiz.html", {'form': form})

def add_question(request):
    questions = Question.objects.all().order_by('-id')
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_question')  # Redirect after POST to prevent duplicate submissions
    else:
        form = QuestionForm()
    return render(request, "add_question.html", {'form': form, 'questions': questions})

def delete_question(request, myid):
    question = get_object_or_404(Question, id=myid)
    if request.method == "POST":
        question.delete()
        return redirect('add_question')
    return render(request, "delete_question.html", {'question': question})

def add_options(request, myid):
    question = get_object_or_404(Question, id=myid)
    QuestionFormSet = inlineformset_factory(Question, Answer, fields=('content', 'correct', 'question'), extra=4)
    
    if request.method == "POST":
        formset = QuestionFormSet(request.POST, instance=question)
        if formset.is_valid():
            formset.save()
            return render(request, "add_options.html", {'alert': True})

    formset = QuestionFormSet(instance=question)
    return render(request, "add_options.html", {'formset': formset, 'question': question})

def results(request):
    marks = Marks_Of_User.objects.all()
    return render(request, "results.html", {'marks': marks})

def delete_result(request, myid):
    marks = get_object_or_404(Marks_Of_User, id=myid)
    if request.method == "POST":
        marks.delete()
        return redirect('results')
    return render(request, "delete_result.html", {'marks': marks})