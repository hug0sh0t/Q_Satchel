import json
from decimal import Decimal
from fractions import Fraction

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver  
# created
from .models import Profile
from pockets.models import Pocket
from .forms import ProfileForm
from .serializers import SharedProfileSerializer
# RESTAPI
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
# from rest_framework import authentication, permissions
from rest_framework import authentication, permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.views import APIView

from allauth.account.models import EmailAddress
from django.views.decorators.http import require_http_methods
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import get_user_model
from django.http import Http404
from django.conf import settings
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from allauth.account.adapter import DefaultAccountAdapter



User = get_user_model()





def nonauto_login_view(request, *args, **kwargs):


    form = AuthenticationForm(request, data=request.POST or None)
    if form.is_valid():
        user_ = form.get_user()
        login(request, user_)

        return redirect("/profiles/analyze/charts")

    context = {
        "form": form,
    }
    
    return render(request, "pages/nonautologin.html", context)


def error_404_view(request, exception):
    return render(request, "404.html")

@receiver(user_logged_in)
def got_online(sender, user, request, **kwargs):    
    user.profile.is_online = True
    user.profile.save()

@receiver(user_logged_out)
def got_offline(sender, user, request, **kwargs):   
    user.profile.is_online = False
    user.profile.save()


def profile_detail_view(request, username, *args, **kwargs): # template for profile detail
    # get profile
    if not request.user.is_authenticated:
        messages.error(request, " Please Login")
        return redirect("/oauth/login")
    qs = Profile.objects.filter(user__username=username)
    if not qs.exists():
        raise Http404

    qsone = qs.first()

    actorqs = Profile.objects.filter(user__username=request.user)
    actorqsone = actorqs.first()

    user_model = User.objects.filter(username=username)
    user_pockets = Pocket.objects.filter(user=request.user)

    
    followers = qsone.followers.all()
    following = qsone.following.all()


    if username in actorqsone.following.all():
      button_action = "UNFOLLOW"
    elif request.user in qsone.followers.all():
      button_action = "UNFOLLOW"
    else:
      button_action = "FOLLOW "
  


    
    djangouser = User.objects.filter(username = username).first()
     
    allauth_email = EmailAddress.objects.filter(user=djangouser.id) # allauth ...  user = the ID 
    context = {"profiles":qs,
    "bus_email": user_model.first().email, 
    "pockets_amount": user_pockets.count(),
    "qsone": qsone,
    "button_action": button_action, 
  
    # "following_avatar_bin": f_avatar_bin,
    "followers_count": followers.count(),
    "following_count":following.count(),
    "username":username, 
    "satchel": qsone.satchel, 
    "pos_satchel": qsone.pos_satchel,
    "neg_satchel": qsone.neg_satchel,
    "oauth_email": allauth_email
    }
    return render(request, "profiles/detail.html", context)

def analyze_view(request, *args, **kwargs): # template for profile detail

    if not request.user.is_authenticated:
        messages.error(request, " Please Login")
        return redirect("/oauth/login")
    qs = Profile.objects.filter(user__username=str(request.user))
    if not qs.exists():
        raise Http404

    qsone = qs.first()


    user_model = User.objects.filter(username=str(request.user))
    user_pockets = Pocket.objects.filter(user=request.user)
    pocket_average = Decimal(0.0)

    satchel = Decimal(0.0) #sum 
    pos_satchel = Decimal(0.0)
    neg_satchel = Decimal(0.0)

    WINS = Decimal(0.0)
    LOSSES = Decimal(0.0)

    bin = []


    for p in user_pockets:
         
        
        if p.currency == "USD":
            satchel += p.price / 1

        if p.price < 0:
            neg_satchel += p.price
            LOSSES += 1 
        elif p.price >= 0:
            pos_satchel += p.price
            WINS += 1
        bin.insert(0, p.price)
        

    if len(bin) > 0:
        pocket_average = satchel/len(bin) # Total Sum / Length of Entire Pocket Array
    elif len(bin) <= 0:
        pocket_average = 0.00
    

    context = {
    "profiles":qs,

    "WINS": WINS,
    "LOSSES": LOSSES,

    "followers_am": qsone.followers.count(),

    "pocketsamount": user_pockets.count(),
    "following_am": qsone.following.count(),
    "bus_email": user_model.first().email, 
    "pockets_amount": user_pockets.count(),

    "qsone": qsone,
    "username":str(request.user), 
    "satchel": round(satchel, 2),

    "pos_satchel": round(pos_satchel , 2),
    "neg_satchel": round(neg_satchel, 2),
    "avg_satchel": round(pocket_average, 2),
    
    }
    return render(request, "profiles/analyze.html", context)


def allocation_view(request, *args, **kwargs): # template for profile detail

    if not request.user.is_authenticated:
        messages.error(request, " Please Login")
        return redirect("/oauth/login")
    qs = Profile.objects.filter(user__username=str(request.user))
    qsone = qs.first()
    user_pockets = Pocket.objects.filter(user=request.user)
    
    if not qs.exists() or not user_pockets.exists():
        raise Http404

    absoluteSatchel = Decimal(0.0) # 
    positiveWeights = []
    negativeWeights = []

    positiveWeightTotal = Decimal(0.0)
    negativeWeightTotal = Decimal(0.0)

    for proxy in user_pockets:
        absoluteSatchel += abs(proxy.price)
    for p in user_pockets:
        if p.price >= 0:      
            positiveWeights.insert(0, (abs(p.price)/int(absoluteSatchel))*100)  
        elif p.price < 0:
            negativeWeights.insert(0, (abs(p.price)/int(absoluteSatchel))*100)
    for posW in positiveWeights:
        positiveWeightTotal += posW 
    for negW in negativeWeights:
        negativeWeightTotal += negW


    context = {
    "profiles":qs,
    "pockets_amount": user_pockets.count(),
    "qsone": qsone,
    "username":str(request.user), 
    "satchel": round(qsone.satchel, 2),
    "pos_satchel": qsone.pos_satchel,
    "neg_satchel": qsone.neg_satchel,
    "positiveWeightTotal": round(positiveWeightTotal, 5),
    "negativeWeightTotal": round(negativeWeightTotal, 5)
    }
    return render(request, "profiles/allocation.html", context)



def profile_update_view(request, *args, **kwargs): # template for profile remodel
    if not request.user.is_authenticated:
        raise Http404
    profileQuery = Profile.objects.all()
    # pquery_obj = profileQuery.first()
    userQ = profileQuery.filter(user=request.user).first()

    user = request.user
    user_data = {
        "first_name": user.first_name,
        "username": user.username,
        "last_name": user.last_name,
        "email": user.email
    }
    my_profile = user.profile
    post_data = request.POST or None 
    file_data = request.FILES or None
    form = ProfileForm(post_data, file_data, instance=my_profile, initial=user_data)
    if form.is_valid():
        profile_obj = form.save(commit=False)
        first_name = form.cleaned_data.get('first_name')
        last_name = form.cleaned_data.get('last_name')
        email = form.cleaned_data.get('email')
        # username = form.cleaned_data.get('username')
        
        # solution
        avatar = form.cleaned_data.get('avatar')

        user.first_name = first_name
        user.last_name = last_name
        #solution

        user.avatar = avatar

        user.email = email

        user.save()
        profile_obj.save()
        messages.success(request, "Changes have been made")

        return redirect('/profiles/edit')
    context = {
        "form": form,
        "mainuser": userQ,
        "profilePicture": userQ.avatar,
        "profiles":profileQuery,

    }
    return render(request, "profiles/remodel.html", context)

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication])
def profile_detail_api_view(request, *args, **kwargs): # profile Detail API endpoint
    # profile query search
    qs = Profile.objects.filter(user__username=request.user.username)
    if not qs.exists():
        return Response({"detail": "Sorry, That Is Not a Known Member"}, status=404)
    profile_obj = qs.first()

    serializer = SharedProfileSerializer(instance=profile_obj, context={"request": request})

    return JsonResponse(serializer.data, status=200)

def updateTheme(request): # CSS toggle Endpoint
    if request.method == 'GET':
        raise Http404
    elif request.method == 'POST':
        data = json.loads(request.body)
        theme = data['theme']
        profile = Profile.objects.filter(user = request.user)
        profile.update(style_value = theme)

    return JsonResponse('Updated', safe=False)





# follow / unfollow system________________________________________



def profile_followers_view(request, username, *args, **kwargs):


    if not request.user.is_authenticated:
        messages.error(request, " Please Login")
        return redirect("/oauth/login")
    qs = Profile.objects.filter(user__username=username)

    if not qs.exists():
        raise Http404
    qsone = qs.first()
    
    followers = qsone.followers.all()
    f_avatar_bin = Profile.objects.none()
    
    for sweep in followers:
      decoy = Profile.objects.filter(user=sweep)
      f_avatar_bin = f_avatar_bin | decoy
    

     

    context = {
      "following_avatar_bin": f_avatar_bin,
      "username": username,
      "subjects_obj": qsone,
    
    }
    return render(request, "profiles/followers.html", context)

def profile_following_view(request, username, *args, **kwargs):


    if not request.user.is_authenticated:
        messages.error(request, " Please Login")
        return redirect("/oauth/login")
    qs = Profile.objects.filter(user__username=username)
    qsone = qs.first()


     
    # message for user doesnt exist
    if not qs.exists():
        raise Http404
    qsone = qs.first()
    
    following = qsone.following.all()
    f_avatar_bin = Profile.objects.none()
    
    for sweep in following:
      decoy = Profile.objects.filter(user=sweep)
      f_avatar_bin = f_avatar_bin | decoy

    context = {
    
      "following_avatar_bin": f_avatar_bin,
      "username": username,
      "subjects_obj": qsone,
    
    }
    return render(request, "profiles/following.html", context)



@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication])
def connection_ToggleEP(request, subject, actor, *args, **kwargs): # FOLLOW UNFOLLOW FUNCTION 

    if request.method == "GET":
        raise Http404
    elif request.method == "POST" and str(subject) != str(actor):
        subject_qs = Profile.objects.filter(user__username = str(subject))
        subject_qsone = subject_qs.first()

        actor_obj = Profile.objects.filter(user__username = str(actor)).first()
        action = "FOLLOW"

            
        if request.user in subject_qsone.followers.all():
            action = "UNFOLLOW"
            subject_qsone.followers.remove(request.user)
            actor_obj.following.remove(subject_qsone.user)
            
        else:
            action = "FOLLOW"
            subject_qsone.followers.add(request.user)
            actor_obj.following.add(subject_qsone.user)
    
        
      
    data = {"subject ":str(subject), 
    "actor":str(actor), 
    "action": str(action), 
    "following_amount": subject_qsone.following.count(),
    "followers_amount": subject_qsone.followers.count()}
    return Response(data)





@require_http_methods(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication])
def remove_account(request):
    user_pk = request.user.pk
    auth_logout(request)
    User = get_user_model()
    User.objects.filter(pk=user_pk).delete()

    messages.info(request, "Your Account has been Successfully Deactivated")
    return redirect('/oauth/login')