
import json
import requests

from decimal import Decimal
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects



from django.shortcuts import render, redirect
from django.db.models import F
from django.db.models import Q
from django import forms
from django.contrib.admin.widgets import AdminDateWidget


from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication 

from django.views.generic import UpdateView
from django.contrib import messages
from django.http import Http404, JsonResponse

from .serializers import (PocketSerializer, PocketCreateSerializer)
from profiles.models import Profile
from .models import Pocket
from .forms import PocketFilter, ProfileFilter
from django.conf import settings


ALLOWED_HOSTS = settings.ALLOWED_HOSTS

class PocketRemodel(UpdateView):# CBV Generic Pocket Update
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    model = Pocket
    
    template_name = "pockets/change.html"
    fields = ["title", "exchange", "summary", "cost_basis", "price", "category", "pocket_time_instance", "receipt", "currency", "direction"]
    proxy = model.objects.all()

 
    def get_context_data(self, **kwargs):
        context = super(PocketRemodel, self).get_context_data(**kwargs)
        pockets = Pocket.objects.filter(id=self.kwargs['pk'])

        context.update({
          'pocket_image': pockets.first().receipt,
          'pocket_PnL': pockets.first().profit_or_loss
          
          })
        return context

    def form_valid(self, form):
        # print the clean form to confirm
  
        return super().form_valid(form)


class ChartData(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        profile = Profile.objects.filter(user=request.user)
        pockets = Pocket.objects.filter(user=request.user).order_by(str(profile.first().order_matrix))

        magnify_profile = profile.first()
        bin = []
        labels = []
        sum_label_insert = []
        sum_bin_insert = []

        dynamicLineColorArray = [] # LINE CHART ARRAY with the color fo the sum inserted at start of array
        dynamicPriceToColorArray = [] # ARRAY OF THE CORRESPONDING COLORS
        hoverdynamicPriceToColorArray = []
        dynamicPercentArray = [] # PERCENTAGE ARRAY FOR ALLOCATION DOUGHNUT
        dynamicPreConversionPercentArray = [] # PERCENTAGE ARRAY FOR ALLOCATION DOUGHNUT


        satchel = Decimal(0.0)
        pos_satchel = Decimal(0.0)
        neg_satchel = Decimal(0.0)
        absoluteSatchel = Decimal(0.0)

        for proxy in pockets:
            absoluteSatchel += abs(proxy.price)

        for p in pockets:

            p.profit_or_loss = p.price-p.cost_basis
            p.save()
            dynamicPreConversionPercentArray.insert(0, round((abs(p.price)/int(absoluteSatchel))*100, 2))
            if p.currency == "USD":
                p.price = p.price * 1 

   


            if p.price >= 0:
                dynamicPriceToColorArray.insert(0,'rgba(80, 196, 74, 0.9)')
                hoverdynamicPriceToColorArray.insert(0,'rgba(80, 196, 74, 0.7)')
                dynamicLineColorArray.insert(0,'rgba(80, 196, 74, 0.9)')  
            elif p.price < 0:
                dynamicPriceToColorArray.insert(0,'rgba(255, 40, 40, 1)')
                hoverdynamicPriceToColorArray.insert(0,'crimson')
                dynamicLineColorArray.insert(0,'rgba(255, 40, 40, 1)')


 
            bin.insert(0, p.price)
            labels.insert(0, p.title)
            satchel += p.price # SUM of everything
            dynamicPercentArray.insert(0, round((abs(p.price)/int(absoluteSatchel))*100, 2))
                         

            sum_label_insert.insert(0, p.title)
            sum_bin_insert.insert(0, p.price)
            
            # Percentage Algorithm 

            if p.price < 0:
                neg_satchel += p.price 
            elif p.price >= 0:
                pos_satchel += p.price
        sum_label_insert.insert(len(sum_bin_insert), "TOTAL SUM")
        sum_bin_insert.insert(len(sum_bin_insert), satchel)
        if satchel >= 0:
            dynamicLineColorArray.insert(0,'rgba(16, 151, 16, 0.9)')  
        else:
            dynamicLineColorArray.insert(0,'rgba(255, 40, 40, 0.8)')
  
        
        profile.update(satchel = satchel)
        profile.update(pos_satchel = pos_satchel)
        profile.update(neg_satchel = neg_satchel)
 
        data = {
            "dynamicPreConversionPercentArray": dynamicPreConversionPercentArray,
            "dynamicPercentArray": dynamicPercentArray,
            "dynamicRBGArray": dynamicPriceToColorArray,
            "hoverdynamicRBGArray": hoverdynamicPriceToColorArray,
            "dynamicLineRBGArray": dynamicLineColorArray,
            "labels": labels,
            "default": bin,
            "satchel": magnify_profile.satchel,
            "labelInsertArray": sum_label_insert,
            "sumInsertArray": sum_bin_insert,
        } 
        return JsonResponse(data)





class AuthMaster(forms.Form):

    
    date_input = forms.DateField(widget=AdminDateWidget())
    receipt = forms.ImageField()
    currency = forms.ChoiceField()


    def index(request,  *args, **kwargs): # Main Page for Authenticated Users
        if not request.user.is_authenticated:
            return redirect('/oauth/login')
                
        profile_qs = Profile.objects.filter(user=request.user)
        oneqs = profile_qs.first()
        user_order_matrix = oneqs.order_matrix        
        pockets = Pocket.objects.filter(user=request.user)
        form = AuthMaster()
        for p in pockets:
            p.profit_or_loss = p.price-(p.cost_basis)
            p.save()
            

        context={

            "form": form,
            "user_order_matrix": user_order_matrix,
            "pockets_amount": pockets.count(),
            "profiles":profile_qs,
            "requested_users_pockets": pockets.all(),

            "satchel_amount": oneqs.satchel,
        }    

        return render(request, "pages/authpockets.html", context, status=200)




def listmode_view(request, *args, **kwargs): # template for profile detail

    pockets = Pocket.objects.filter(user=request.user)

    context = {
      "pockets_amount": pockets.count(),
      "requested_users_pockets": pockets.all(),
    }
    return render(request, "pockets/listmode.html", context)

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def pocket_create_view(request, *args, **kwargs): # Creation of Pocket
    serializer = PocketCreateSerializer(data=request.POST)
    if serializer.is_valid(raise_exception=True):
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)

    return Response({}, status=400)


# Authorized Profile View 
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def pocket_detail_view(request, pocket_id, *args, **kwargs): # Pocket Detail ENDPOINT
    qs = Pocket.objects.filter(id=pocket_id)
    if not qs.exists():
        return Response({}, status=404)
    if not qs.exists():
        return Response({}, status=404)
    serializer = PocketSerializer(qs, many=True)
    return Response(serializer.data, status=200)

@api_view(['GET','POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def full_pocket_delete_view(request):
    pockets = Pocket.objects.filter(user=request.user)


    if request.method == 'POST':
        for p in pockets:
            p.delete()
        messages.error(request, "All Pockets Deleted")
        return redirect("/")
    data = {
        "user": str(request.user)
    }

    return Response(data)

# Req to API > Redirect to home
@api_view(['POST', 'GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def pocket_delete_view(request, pocket_id, *args, **kwargs):
    qs = Pocket.objects.filter(id=pocket_id)
    if not qs.exists():
        return Response({}, status=404)
    uqs = qs.filter(user = request.user)
    if not uqs.exists():
        return Response({"message":"UnAuthorized Delete"}, status=401)

    if request.method == 'POST':
        
        obj = qs.first()
        obj.delete()
        if str(request.headers.get('referer')) == "https://qsatchel.com/pockets/deepdive":
            messages.error(request, "Trade deleted ")
            return redirect('/pockets/deepdive')

        elif str(request.headers.get('referer')) == "https://qsatchel.com/":
            messages.error(request, "Trade deleted")         
            return redirect('/')
        else: 
            return redirect('/') 

    
    if request.method == 'GET':
        raise Http404
    return Response({"message":"No proper Requests have been Submitted, you may not proceed"}, status=200)


# /api/pockets
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication])
def api_pocket_list_view(request, *args, **kwargs):
    username = request.GET.get('username')
    profile_qs = Profile.objects.filter(user=request.user)
    pqs_first = profile_qs.first()
    
    if request.method == 'POST':
        for value in request.POST.items():    
            choice = value 

        if choice[1] == '-price':
            profile_qs.update(order_matrix='-price')
            return redirect('/')
        elif choice[1] == 'price':
            profile_qs.update(order_matrix = 'price')
            return redirect('/')
        elif choice[1] == 'pocket_time_instance':
            profile_qs.update(order_matrix = 'pocket_time_instance')
            return redirect('/')
        elif choice[1] == '-pocket_time_instance':
            profile_qs.update(order_matrix = '-pocket_time_instance')
            return redirect('/')
        elif choice[1] == 'title':
            profile_qs.update(order_matrix = 'title')
            return redirect('/')
        elif choice[1] == '-title':
            profile_qs.update(order_matrix = '-title')
            return redirect('/')
    qs = Pocket.objects.filter(user=request.user).order_by(str(pqs_first.order_matrix))
    if username != None:
        qs = qs.by_username(username)


    serializer = PocketSerializer(qs, many=True)
    return Response(serializer.data, status=200)

# /pockets needed for creation
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def pocket_list_view(request, *args, **kwargs):
    # qs = Pocket.objects.filter(user = request.user)
    qs = Pocket.objects.filter(user=request.user)
    username = request.GET.get('username')
    if not request.user.is_authenticated:
        return redirect("/oauth/manual/login/")
    if username != None:
        qs = qs.by_username(username)
    serializer = PocketSerializer(qs, many=True)
    return Response(serializer.data, status=200)

def profile_search_view(request, pocketquery): # Search Using a template and Re-Rendering
    userspockets = Pocket.objects.filter(user=request.user)
    userprofile = Profile.objects.all()
    # ordered_pockets = post.comments.filter(active=True).annotate(comraw=Count('commentlike')).order_by("-comraw")
    u = ProfileFilter(request.GET, queryset=userprofile.filter(
        Q(user__username__contains=str(pocketquery))|
        Q(user__first_name__contains=str(pocketquery))|
        Q(user__last_name__contains=str(pocketquery))))

    n = PocketFilter(request.GET,queryset=userspockets.filter(
        Q(title__contains=str(pocketquery))|
        Q(price__contains=str(pocketquery))|
        Q(category__contains=str(pocketquery))|
        Q(summary__contains=str(pocketquery))|
        Q(currency__contains=str(pocketquery))))
        
    
    search_q = request.POST.get('valuebox', None)
    if search_q:
         return redirect("/search/"+search_q)
    context = {
            "query": pocketquery,
            "nogfilter": n,
            "profilter": u
    } 
    return render(request, "pockets/search.html", context)


