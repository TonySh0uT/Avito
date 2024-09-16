from rest_framework import serializers
from .models import Tender, Bid, BidReview


class TenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tender
        fields = ('id', 'name', 'description', 'status', 'serviceType', 'version', 'createdAt')


class BidsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ('id', 'name', 'description', 'status', 'authorType', 'authorId', 'version', 'createdAt')

class ReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BidReview
        fields = ('id', 'description', 'createdAt')
