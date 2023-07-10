import requests
import json

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

# import related models here
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print(f"GET from {url}")
    try:
        response = requests.get(url, headers={"Content-Type": "application/json"}, params=kwargs)
    except:
        print("Network exception occurred")
    status_code = response.status_code
    print(f"With status {status_code}")
    json_data = json.loads(response.text)
    return json_data


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    json_result = get_request(url, **kwargs)
    if json_result:
        dealers = json_result
        for dealer in dealers:
            dealer_doc = dealer["doc"]
            dealer_obj = CarDealer(
                address=dealer_doc["address"],
                city=dealer_doc["city"],
                full_name=dealer_doc["full_name"],
                id=dealer_doc["id"],
                lat=dealer_doc["lat"],
                long=dealer_doc["long"],
                short_name=dealer_doc["short_name"],
                st=dealer_doc["st"],
                zip=dealer_doc["zip"]
            )
            results.append(dealer_obj)

    return results


def get_dealer_by_id(url, dealer_id):
    result = None
    json_result = get_request(url, id=dealer_id)
    if json_result:
        dealer = json_result[0]
        result = CarDealer(
            address=dealer["address"],
            city=dealer["city"],
            full_name=dealer["full_name"],
            id=dealer["id"],
            lat=dealer["lat"],
            long=dealer["long"],
            short_name=dealer["short_name"],
            st=dealer["st"],
            zip=dealer["zip"]
        )

    return result


def get_dealer_by_state(url, state):
    results = []
    json_result = get_request(url, st=state)
    if json_result:
        dealers = json_result
        for dealer in dealers:
            dealer_obj = CarDealer(
                address=dealer["address"],
                city=dealer["city"],
                full_name=dealer["full_name"],
                id=dealer["id"],
                lat=dealer["lat"],
                long=dealer["long"],
                short_name=dealer["short_name"],
                st=dealer["st"],
                zip=dealer["zip"]
            )
            results.append(dealer_obj)

    return results


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, **kwargs):
    results = []
    dealer_id = kwargs.get("dealer_id")
    if id:
        json_result = get_request(url, id=dealer_id)
    else:
        json_result = get_request(url)

    if json_result:
        reviews = json_result["data"]["docs"]
        for review in reviews:
            review_obj = DealerReview(
                dealership=review["dealership"],
                name=review["name"],
                purchase=review["purchase"],
                review=review["review"],
                purchase_date=review["purchase_date"],
                car_make=review["car_make"],
                car_model=review["car_model"],
                car_year=review["car_year"],
                sentiment=None,
                id=review["id"]
            )
            review_obj.sentiment = analyze_review_sentiments(review_obj.review)
            results.append(review_obj)

    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text):
    # print(text)
    url = "https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/20fbf20b-c2d8-45ed-b32e-389f8a79033c"
    api_key = "_OPzI3nGS7mBhw49vBRsT4GemW24VUSwc4v7dbyliESZ"
    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(version="2022-04-07",
                                                                    authenticator=authenticator)
    natural_language_understanding.set_service_url(url)
    # using text*3 as the analysis target, in case of getting following errors:
    # ibm_cloud_sdk_core.api_exception.ApiException: Error: not enough text for language id, Code: 422
    # ibm_cloud_sdk_core.api_exception.ApiException: Error: target(s) not found, Code: 400
    response = natural_language_understanding.analyze(
        text=text * 3,
        features=Features(sentiment=SentimentOptions(targets=[text * 3]))
    ).get_result()
    # print(json.dumps(response, indent=2))
    label = response["sentiment"]["document"]["label"]
    print(label)
    return label
