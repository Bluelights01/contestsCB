from django.shortcuts import render,redirect
from .models import Students,Contest,IsLogin,ContestLeaderboard
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from datetime import datetime
import pytz
import json
from django.utils.dateparse import parse_date
from django.core.serializers.json import DjangoJSONEncoder
from . import fetch

myvar=""

def members(request):
    return redirect('home')


def register(request):
    
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return render(request, 'register.html', {'error': 'Passwords do not match!'})
        
        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'register.html', {'error': 'Invalid email address!'})

        if Students.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': 'Email already registered!'})
        Students.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )
        return redirect('login')

   
    return render(request,'register.html')
def login(request):
    
    email=request.POST.get("email")
    password=request.POST.get("password")
    userleet=request.POST.get("LeetcodeID")
    if(email==password):
        return render(request,'login.html')
    if not Students.objects.filter(email=email).exists():
        return render(request,'login.html',{'error': 'Email not found'})
    mystudent=Students.objects.get(email=email)
    if(mystudent.password!=password):
        return render(request,'login.html',{'error': 'incorrect password or Mail'})
    if(mystudent.password==password):

        return redirect(f'/home/?leetcode_id={userleet}')
    return render(request,'login.html')
def home(request):
    ist = pytz.timezone('Asia/kolkata')
    now_ist = datetime.now(ist)
    ques1=0
    ques2=0
    ques3=0
    today_ist = now_ist.date()
    contest = Contest.objects.filter(date=today_ist).first() 
    myvar=request.GET.get('leetcode_id')
    if(contest==None):
        latest_date = ContestLeaderboard.objects.latest('contest_date').contest_date
        
        # Get all entries for that date
        latest_entries = ContestLeaderboard.objects.filter(contest_date=latest_date)
        data = list(latest_entries.values(
            'contest_name', 
            'user_name', 
            'marks', 
            'question1', 
            'question2', 
            'question3', 
            'contest_date'
        ))
        entrylist_json = json.dumps(data, cls=DjangoJSONEncoder)
        context = {
        'myvar': myvar,
        'start': None,
        'entrylist_json': entrylist_json  # <-- Add this line
        }
        print(entrylist_json)
        return render(request, 'home.html', context)
    curr_ti=now_ist.time()
    start=0
     

    start_ti=contest.start_time
    end_ti=contest.end_time
   
    if request.method == "POST":
        if "verify" in request.POST:
            task1=fetch.get_latest_submissions(myvar,10)
            mylist=fetch.display_solved_questions(task1,myvar,10)

            ques1=contest.question_1
            ques2=contest.question_2
            ques3=contest.question_3
            marks=0
            if(ques1 in mylist):
                ques1=1
                marks+=100
            else:
                ques1=0
            if(ques2 in mylist):
                ques2=1
                marks+=100
            else:
                ques2=0
            if(ques3 in mylist):
                marks+=100
                ques3=1
            else:
                ques3=0
            
            entry=ContestLeaderboard.objects.update_or_create(
            contest_name = contest.name,
            user_name = myvar,
            contest_date = today_ist,
            defaults={
                'marks':marks,
                'question1':ques1,
                'question2':ques2,
                'question3':ques3,
            }
            )
            
    if(curr_ti>=start_ti and curr_ti<=end_ti):
        start=1


    return render(request,'home.html',{'contest': contest,'myvar':myvar,'start':start,'ques1':ques1,
                                       'ques2':ques2,'ques3':ques3})
def newhome(request,leetcode_id):
    ist = pytz.timezone('Asia/Kolkata')
    
    now_ist = datetime.now(ist)

    today_ist = now_ist.date()
    
    contest = Contest.objects.filter(date=today_ist).first()  

