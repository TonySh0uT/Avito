"""
URL configuration for tender_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from tenders.views import TenderCreateAPIView, PingAPIView, TendersGetAPIView, TendersGetMyAPIView, \
    TendersGetOrPutStatusAPIView, TendersEditAPIView, TendersRollbackAPIView, BidsCreateAPIView, BidsGetMyAPIView, \
    BidsGetListAPIView, BidsGetOrPutStatusAPIView, BidsEditAPIView, BidsRollbackAPIView, BidsPutReviewAPIView, \
    BidsReviewsAPIView, BidsDecisionsAPIView

urlpatterns = [
    path('admin/', admin.site.urls),


    path('api/ping', PingAPIView.as_view()),
    path('api/tenders/new', TenderCreateAPIView.as_view()),
    path('api/tenders', TendersGetAPIView.as_view()),
    path('api/tenders/my', TendersGetMyAPIView.as_view()),
    path('api/tenders/<str:tender_id>/status', TendersGetOrPutStatusAPIView.as_view()),
    path('api/tenders/<str:tender_id>/edit', TendersEditAPIView.as_view()),
    path('api/tenders/<str:tender_id>/rollback/<int:version>', TendersRollbackAPIView.as_view()),

    path('api/bids/new', BidsCreateAPIView.as_view()),
    path('api/bids/my', BidsGetMyAPIView.as_view()),
    path('api/bids/<str:tender_id>/list', BidsGetListAPIView.as_view()),
    path('api/bids/<str:bid_id>/status', BidsGetOrPutStatusAPIView.as_view()),
    path('api/bids/<str:bid_id>/edit', BidsEditAPIView.as_view()),
    path('api/bids/<str:bid_id>/rollback/<int:version>', BidsRollbackAPIView.as_view()),
    path('api/bids/<str:bid_id>/feedback', BidsPutReviewAPIView.as_view()),
    path('api/bids/<str:tender_id>/reviews', BidsReviewsAPIView.as_view()),
    path('api/bids/<str:bid_id>/submit_decision', BidsDecisionsAPIView.as_view()),

]
