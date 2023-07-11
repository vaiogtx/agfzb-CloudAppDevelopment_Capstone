from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_by_id, get_dealer_by_state, get_dealer_reviews_from_cf, \
    post_request

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    return render(request, "djangoapp/about.html")


# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, "djangoapp/contact.html")


# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')


# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(username))
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)


# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/9b35b474-b8b3-41bf-b868-020942359cb1/dealership-package/get-dealership"
        dealerships = get_dealers_from_cf(url)
        dealer_names = " ".join([dealer.short_name for dealer in dealerships])
        return HttpResponse(dealer_names)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/9b35b474-b8b3-41bf-b868-020942359cb1/dealership-package/get-review"
        reviews = get_dealer_reviews_from_cf(url, dealer_id=dealer_id)
        result = "\n".join([f"{review}[{review.sentiment}]" for review in reviews])

        return HttpResponse(result)


# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    context = {}
    # url = "https://us-south.functions.appdomain.cloud/api/v1/web/9b35b474-b8b3-41bf-b868-020942359cb1/dealership-package/get-dealership"
    url = "https://us-south.functions.appdomain.cloud/api/v1/web/9b35b474-b8b3-41bf-b868-020942359cb1/dealership-package/post-review"
    dealer = get_dealer_by_id(url, dealer_id)
    if request.method == "GET":
        return render(request, "djangoapp/add_review.html", context)
    elif request.method == "POST" and request.user.is_authenticated:
        json_payload = {
            "review": {
                "id": 1117,
                "name": request.user.username,
                "dealership": dealer_id,
                # "review": request.POST["content"],
                "review": "testing post_request",
                "purchase": bool(request.POST.get("purchase", False)),
                "another": "field",
                "purchase_date": datetime.strptime(request.POST["purchase_date"], "%m/%d/%Y").isoformat(),
                # "car_make": car.make.name,
                "car_make": "Audi",
                # "car_model": car.name,
                "car_model": "TT",
                # "car_year": car.year.strftime("%Y"),
                "car_year": 2023

            }
        }
        post_request(url, json_payload, dealer_id=dealer_id)  # dealer_id 有沒有送好像沒差
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
