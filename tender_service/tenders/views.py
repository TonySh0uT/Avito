import rest_framework
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse

from .models import Tender, Employee, Organization, OrganizationResponsible, TenderVersion, Bid, BidVersion, BidReview, \
    BidDecision
from .serializers import TenderSerializer, BidsSerializer, ReviewsSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView


class PingAPIView(APIView):
    def get(self, request):
        return Response('ok', content_type='text/plain', status=status.HTTP_200_OK)


class TenderCreateAPIView(APIView):
    def post(self, request):
        try:
            organization = Organization.objects.get(id=request.data.get('organizationId'))
            employee = Employee.objects.get(username=request.data.get('creatorUsername'))
            if employee.is_responsible_for(organization):
                tender = Tender.objects.create(
                    name=request.data.get('name'),
                    description=request.data.get('description'),
                    serviceType=request.data.get('serviceType').capitalize(),
                    status=request.data.get('status').capitalize(),
                    organization_id=organization,
                    creator_id=Employee.objects.get(username=request.data.get('creatorUsername'))
                )
                return JsonResponse(status=rest_framework.status.HTTP_200_OK, data=TenderSerializer(tender).data)

            return Response(status=rest_framework.status.HTTP_403_FORBIDDEN,
                            data={'reason': 'You do not have permission to do that'})
        except Exception as e:
            return Response(status=rest_framework.status.HTTP_400_BAD_REQUEST, data={'reason': str(e)})


class TendersGetMyAPIView(APIView):
    def get(self, request):
        try:
            tenders = Tender.objects.all()
            username = self.request.query_params.get('username', None)
            user = Employee.objects.get(username=username)
            if username:
                tenders = tenders.filter(
                    Q(organization_id__organizationresponsible__user=user) | Q(status='PUBLISHED')
                ).distinct()
                limit = int(self.request.query_params.get('limit', 5))
                offset = int(self.request.query_params.get('offset', 0))
                tenders = tenders[offset:offset + limit]
                return JsonResponse(status=rest_framework.status.HTTP_200_OK,
                                    data=TenderSerializer(tenders, many=True).data, safe=False)
            else:
                return Response(status=rest_framework.status.HTTP_400_BAD_REQUEST,
                                data={'reason': "Username is required"})
        except Exception as e:
            return Response(status=rest_framework.status.HTTP_400_BAD_REQUEST, data={'reason': str(e)})


class TendersGetAPIView(APIView):
    def get(self, request):
        try:
            tenders = Tender.objects.all()
            service_type = self.request.query_params.get('service_type', None)
            if service_type:
                tenders = tenders.filter(serviceType=service_type.capitalize())
            limit = int(self.request.query_params.get('limit', 5))
            offset = int(self.request.query_params.get('offset', 0))
            tenders = tenders[offset:offset + limit]
            return JsonResponse(status=rest_framework.status.HTTP_200_OK,
                                data=TenderSerializer(tenders, many=True).data, safe=False)
        except Exception as e:
            return Response(status=rest_framework.status.HTTP_400_BAD_REQUEST, data={'reason': str(e)})


class TendersGetOrPutStatusAPIView(APIView):
    def get(self, request, tender_id):
        try:
            username = self.request.query_params.get('username', None)
            tender = Tender.objects.get(id=tender_id)
            if username:
                user = Employee.objects.get(username=username)
                organization = Organization.objects.get(id=tender.organization_id_id)
            if tender.status != 'Published' and username:
                if (user.is_responsible_for(organization)):
                    return JsonResponse(status=rest_framework.status.HTTP_200_OK, data=tender.status, safe=False)
                else:
                    return Response(status=rest_framework.status.HTTP_403_FORBIDDEN,
                                    data={'reason': 'You are not allowed to do this'})
            elif (tender.status == 'Published'):
                return JsonResponse(status=rest_framework.status.HTTP_200_OK, data=tender.status, safe=False)
            else:
                return JsonResponse(status=rest_framework.status.HTTP_403_FORBIDDEN,
                                    data={
                                        'reason': 'You are not allowed to do this, please send username as parameter'})
        except Exception as e:
            return JsonResponse(status=rest_framework.status.HTTP_400_BAD_REQUEST, data={'reason': str(e)})

    def put(self, request, tender_id):
        try:
            username = self.request.query_params.get('username', None)
            new_status = self.request.query_params.get('status', None)
            tender = Tender.objects.get(id=tender_id)
            if username and new_status:
                user = Employee.objects.get(username=username)
                organization = Organization.objects.get(id=tender.organization_id_id)
                if (user.is_responsible_for(organization)):
                    tender.status = new_status.capitalize()
                    tender.save()
                    return JsonResponse(status=rest_framework.status.HTTP_200_OK, data=TenderSerializer(tender).data)
                else:
                    return JsonResponse(status=rest_framework.status.HTTP_403_FORBIDDEN,
                                        data={'reason': 'You are not allowed to do this'})
            else:
                return JsonResponse(status=rest_framework.status.HTTP_400_BAD_REQUEST,
                                    data={
                                        'reason': 'You can not do this, please send username and/or status as parameter'})
        except Exception as e:
            return JsonResponse(status=rest_framework.status.HTTP_400_BAD_REQUEST, data={'reason': str(e)})


class TendersEditAPIView(APIView):
    def patch(self, request, tender_id):
        try:
            username = self.request.query_params.get('username', None)
            tender = Tender.objects.get(id=tender_id)
            if username:
                user = Employee.objects.get(username=username)
                organization = Organization.objects.get(id=tender.organization_id_id)
                if (user.is_responsible_for(organization)):
                    data = request.data
                    with transaction.atomic():
                        TenderVersion.objects.create(
                            tender=tender,
                            name=tender.name,
                            description=tender.description,
                            serviceType=tender.serviceType,
                            status=tender.status,
                            createdAt=tender.createdAt,
                            version=tender.version,
                            organization_id=tender.organization_id,
                            creator_id=tender.creator_id,
                        )

                        if 'name' in data:
                            tender.name = data['name']
                        if 'description' in data:
                            tender.description = data['description']
                        if 'serviceType' in data:
                            tender.serviceType = data['serviceType'].capitalize()
                        if 'status' in data:
                            tender.status = data['status']

                        tender.version += 1
                        tender.save()
                    return JsonResponse(status=rest_framework.status.HTTP_200_OK, data=TenderSerializer(tender).data)
                else:
                    return JsonResponse(status=rest_framework.status.HTTP_403_FORBIDDEN,
                                        data={'reason': 'You are not allowed to do this'})
            else:
                return JsonResponse(status=rest_framework.status.HTTP_400_BAD_REQUEST,
                                    data={
                                        'reason': 'You can not do this, please send username as parameter'})
        except Exception as e:
            return JsonResponse(status=rest_framework.status.HTTP_400_BAD_REQUEST, data={'reason': str(e)})


class TendersRollbackAPIView(APIView):
    def put(self, request, tender_id, version):
        try:
            username = self.request.query_params.get('username', None)
            tender = Tender.objects.get(id=tender_id)
            if username:
                user = Employee.objects.get(username=username)
                organization = Organization.objects.get(id=tender.organization_id_id)
                if (user.is_responsible_for(organization)):
                    with transaction.atomic():
                        TenderVersion.objects.create(
                            tender=tender,
                            name=tender.name,
                            description=tender.description,
                            serviceType=tender.serviceType,
                            status=tender.status,
                            createdAt=tender.createdAt,
                            version=tender.version,
                            organization_id=tender.organization_id,
                            creator_id=tender.creator_id,
                        )
                        needed_version = TenderVersion.objects.get(tender=tender, version=version)
                        tender.name = needed_version.name
                        tender.description = needed_version.description
                        tender.serviceType = needed_version.serviceType
                        tender.status = needed_version.status
                        tender.createdAt = needed_version.createdAt
                        tender.version += 1
                        tender.save()
                    return JsonResponse(status=rest_framework.status.HTTP_200_OK, data=TenderSerializer(tender).data)
                else:
                    return JsonResponse(status=rest_framework.status.HTTP_403_FORBIDDEN,
                                        data={'reason': 'You are not allowed to do this'})
            else:
                return JsonResponse(status=rest_framework.status.HTTP_400_BAD_REQUEST,
                                    data={
                                        'reason': 'You can not do this, please send username as parameter'})
        except Exception as e:
            return JsonResponse(status=rest_framework.status.HTTP_400_BAD_REQUEST, data={'reason': str(e)})


class BidsCreateAPIView(APIView):
    def post(self, request):
        try:
            tender = Tender.objects.get(id=request.data.get('tenderId'))
            author = Employee.objects.get(username=request.data.get('creatorUsername'))
            if author.is_responsible_for_any_organization():
                author_type = 'Organization'
            else:
                author_type = 'User'
            bid = Bid.objects.create(
                name=request.data.get('name'),
                description=request.data.get('description'),
                status=request.data.get('status').capitalize(),
                tenderId=tender,
                authorId=author,
                authorType=author_type
            )
            return JsonResponse(status=rest_framework.status.HTTP_200_OK, data=BidsSerializer(bid).data)

        except Exception as e:
            return Response(status=rest_framework.status.HTTP_400_BAD_REQUEST, data={'reason': str(e)})


class BidsGetMyAPIView(APIView):
    def get(self, request):
        try:
            bids = Bid.objects.all()
            username = self.request.query_params.get('username', None)
            user = Employee.objects.get(username=username)
            organization_ids = list(
                OrganizationResponsible.objects.filter(user=user).values_list('organization_id', flat=True))
            if username:
                bids = bids.filter(
                    Q(authorId__username=username) | Q(tenderId_id__organization_id__in=organization_ids)
                ).distinct()
                limit = int(self.request.query_params.get('limit', 5))
                offset = int(self.request.query_params.get('offset', 0))
                bids = bids[offset:offset + limit]
                return JsonResponse(status=rest_framework.status.HTTP_200_OK, data=BidsSerializer(bids, many=True).data,
                                    safe=False)
            else:
                return Response(status=rest_framework.status.HTTP_400_BAD_REQUEST,
                                data={'reason': "Username is required"})
        except Exception as e:
            return Response(status=rest_framework.status.HTTP_400_BAD_REQUEST, data={'reason': str(e)})


class BidsGetListAPIView(APIView):
    def get(self, request, tender_id):
        try:
            bids = Bid.objects.all()
            username = self.request.query_params.get('username', None)
            user = Employee.objects.get(username=username)
            organization_ids = list(
                OrganizationResponsible.objects.filter(user=user).values_list('organization_id', flat=True))
            if username:
                tender = Tender.objects.get(id=tender_id)
                if (tender.status != 'Closed' and tender.status != 'Created') or user.is_responsible_for(
                        tender.organization_id):
                    bids = bids.filter(
                        Q(authorId__username=username) | Q(tenderId_id__organization_id__in=organization_ids)
                    ).distinct()
                    bids.filter(tenderId=tender_id)
                else:
                    return Response(status=rest_framework.status.HTTP_400_BAD_REQUEST,
                                    data={'reason': "You cannot do  this"})

                limit = int(self.request.query_params.get('limit', 5))
                offset = int(self.request.query_params.get('offset', 0))
                bids = bids[offset:offset + limit]
                return JsonResponse(status=rest_framework.status.HTTP_200_OK, data=BidsSerializer(bids, many=True).data,
                                    safe=False)
            else:
                return Response(status=rest_framework.status.HTTP_400_BAD_REQUEST,
                                data={'reason': "Username is required"})
        except Exception as e:
            return Response(status=rest_framework.status.HTTP_400_BAD_REQUEST, data={'reason': str(e)})


class BidsGetOrPutStatusAPIView(APIView):
    def get(self, request, bid_id):
        try:
            username = self.request.query_params.get('username', None)
            bid = Bid.objects.get(id=bid_id)
            if username:
                user = Employee.objects.get(username=username)
                organization = Organization.objects.get(id=bid.tenderId.organization_id_id)
                if (user.is_responsible_for(organization) or bid.authorId.username == username):
                    return JsonResponse(status=rest_framework.status.HTTP_200_OK, data=bid.status, safe=False)
                else:
                    return Response(status=rest_framework.status.HTTP_403_FORBIDDEN,
                                    data={'reason': 'You are not allowed to do this'})
            else:
                return JsonResponse(status=rest_framework.status.HTTP_403_FORBIDDEN,
                                    data={
                                        'reason': 'You are not allowed to do this, please send username as parameter'})
        except Exception as e:
            return JsonResponse(status=rest_framework.status.HTTP_400_BAD_REQUEST, data={'reason': str(e)})

    def put(self, request, bid_id):
        try:
            username = self.request.query_params.get('username', None)
            new_status = self.request.query_params.get('status', None)
            if new_status == 'Approved' or new_status == 'Rejected':
                return JsonResponse(status=rest_framework.status.HTTP_403_FORBIDDEN,
                                    data={'reason': 'You are not allowed to do this'})
            bid = Bid.objects.get(id=bid_id)
            if username and new_status:
                if bid.authorId.username == username and bid.status != 'Approved' and bid.status != 'Rejected':
                    bid.status = new_status.capitalize()
                    bid.save()
                    return JsonResponse(status=rest_framework.status.HTTP_200_OK, data=BidsSerializer(bid).data)
                else:
                    return JsonResponse(status=rest_framework.status.HTTP_403_FORBIDDEN,
                                        data={'reason': 'You are not allowed to do this'})
            else:
                return JsonResponse(status=rest_framework.status.HTTP_400_BAD_REQUEST,
                                    data={
                                        'reason': 'You can not do this, please send username and/or status as parameter'})
        except Exception as e:
            return JsonResponse(status=rest_framework.status.HTTP_400_BAD_REQUEST, data={'reason': str(e)})


class BidsEditAPIView(APIView):
    def patch(self, request, bid_id):
        try:
            username = self.request.query_params.get('username', None)
            bid = Bid.objects.get(id=bid_id)
            if username:
                if bid.authorId.username == username and bid.status != 'Approved' and bid.status != 'Rejected':
                    data = request.data
                    with transaction.atomic():
                        BidVersion.objects.create(
                            bid=bid,
                            name=bid.name,
                            description=bid.description,
                            status=bid.status,
                            tenderId=bid.tenderId,
                            authorType=bid.authorType,
                            authorId=bid.authorId,
                            version=bid.version,
                            createdAt=bid.createdAt,
                        )
                        if 'name' in data:
                            bid.name = data['name']
                        if 'description' in data:
                            bid.description = data['description']
                        if 'status' in data:
                            bid.status = data['status']
                        bid.version += 1
                        bid.save()
                    return JsonResponse(status=rest_framework.status.HTTP_200_OK, data=BidsSerializer(bid).data)
                else:
                    return JsonResponse(status=rest_framework.status.HTTP_403_FORBIDDEN,
                                        data={'reason': 'You are not allowed to do this'})
            else:
                return JsonResponse(status=rest_framework.status.HTTP_400_BAD_REQUEST,
                                    data={
                                        'reason': 'You can not do this, please send username and/or status as parameter'})
        except Exception as e:
            return JsonResponse(status=rest_framework.status.HTTP_400_BAD_REQUEST, data={'reason': str(e)})


class BidsRollbackAPIView(APIView):
    def put(self, request, bid_id, version):
        try:
            username = self.request.query_params.get('username', None)
            bid = Bid.objects.get(id=bid_id)
            if username:
                if bid.authorId.username == username and bid.status != 'Approved' and bid.status != 'Rejected':
                    with transaction.atomic():
                        BidVersion.objects.create(
                            bid=bid,
                            name=bid.name,
                            description=bid.description,
                            status=bid.status,
                            tenderId=bid.tenderId,
                            authorType=bid.authorType,
                            authorId=bid.authorId,
                            version=bid.version,
                            createdAt=bid.createdAt,
                        )
                        needed_version = BidVersion.objects.get(bid=bid, version=version)
                        bid.name = needed_version.name
                        bid.description = needed_version.description
                        bid.status = needed_version.status
                        bid.tenderId = needed_version.tenderId
                        bid.authorType = needed_version.authorType
                        bid.authorId = needed_version.authorId
                        bid.createdAt = needed_version.createdAt
                        bid.version += 1
                        bid.save()
                    return JsonResponse(status=rest_framework.status.HTTP_200_OK, data=BidsSerializer(bid).data)
                else:
                    return JsonResponse(status=rest_framework.status.HTTP_403_FORBIDDEN,
                                        data={'reason': 'You are not allowed to do this'})
            else:
                return JsonResponse(status=rest_framework.status.HTTP_400_BAD_REQUEST,
                                    data={
                                        'reason': 'You can not do this, please send username and/or status as parameter'})
        except Exception as e:
            return JsonResponse(status=rest_framework.status.HTTP_400_BAD_REQUEST, data={'reason': str(e)})


class BidsPutReviewAPIView(APIView):

    def put(self, request, bid_id):
        try:
            username = self.request.query_params.get('username', None)
            bid_feedback = self.request.query_params.get('bidFeedback', None)

            bid = Bid.objects.get(id=bid_id)
            if username and bid_feedback:
                user = Employee.objects.get(username=username)
                organization = Organization.objects.get(id=bid.tenderId.organization_id_id)
            else:
                return JsonResponse(status=rest_framework.status.HTTP_400_BAD_REQUEST,
                                    data={
                                        'reason': 'You can not do this, please send username and/or feedback as parameter'})
            if not user.is_responsible_for(organization):
                return JsonResponse(status=rest_framework.status.HTTP_403_FORBIDDEN,
                                    data={'reason': 'You are not allowed to do this'})
            else:
                BidReview.objects.create(description=bid_feedback, bid=bid, author=user)
                return JsonResponse(status=rest_framework.status.HTTP_200_OK, data=BidsSerializer(bid).data)
        except Exception as e:
            return JsonResponse(status=rest_framework.status.HTTP_400_BAD_REQUEST, data={'reason': str(e)})


class BidsReviewsAPIView(APIView):
    def get(self, request, tender_id):
        try:
            author_username = self.request.query_params.get('authorUsername', None)
            if author_username:
                author = Employee.objects.get(username=author_username)
            else:
                return JsonResponse(status=rest_framework.status.HTTP_400_BAD_REQUEST,
                                    data={
                                        'reason': 'You can not do this, please send author username as parameter'})
            username = self.request.query_params.get('requesterUsername', None)
            tender = Tender.objects.get(id=tender_id)
            authors_list = tender.get_bid_authors()

            if author not in authors_list:
                return JsonResponse(status=rest_framework.status.HTTP_400_BAD_REQUEST,
                                    data={
                                        'reason': 'This author did not make bids to your tender'})
            if username:
                user = Employee.objects.get(username=username)
                organization = Organization.objects.get(id=tender.organization_id_id)
                if (user.is_responsible_for(organization)):
                    reviews = BidReview.objects.filter(bid__authorId=author)
                    limit = int(self.request.query_params.get('limit', 5))
                    offset = int(self.request.query_params.get('offset', 0))
                    reviews = reviews[offset:offset + limit]
                    return JsonResponse(status=rest_framework.status.HTTP_200_OK,
                                        data=ReviewsSerializer(reviews, many=True).data, safe=False)
                else:
                    return JsonResponse(status=rest_framework.status.HTTP_403_FORBIDDEN,
                                        data={'reason': 'You are not allowed to do this'})
            else:
                return JsonResponse(status=rest_framework.status.HTTP_400_BAD_REQUEST,
                                    data={
                                        'reason': 'You can not do this, please send username as parameter'})
        except Exception as e:
            return JsonResponse(status=rest_framework.status.HTTP_400_BAD_REQUEST, data={'reason': str(e)})


class BidsDecisionsAPIView(APIView):
    def put(self, request, bid_id):
        try:
            username = self.request.query_params.get('username', None)
            decision = self.request.query_params.get('decision', None)

            if username and decision:
                author = Employee.objects.get(username=username)
            else:
                return JsonResponse(status=rest_framework.status.HTTP_400_BAD_REQUEST,
                                    data={
                                        'reason': 'You can not do this, please send username and/or decision as parameter'})
            bid = Bid.objects.get(id=bid_id)
            if bid.tenderId.status == 'Closed':
                return JsonResponse(status=rest_framework.status.HTTP_400_BAD_REQUEST,
                                    data={'reason': 'Tender is closed'})
            if username:
                user = Employee.objects.get(username=username)
                organization = Organization.objects.get(id=bid.tenderId.organization_id_id)
                tender = Tender.objects.get(id=bid.tenderId_id)
                if (user.is_responsible_for(organization)):
                    BidDecision.objects.create(bid=bid, decision=decision, author=author)
                    if decision == 'Rejected':
                        bid.status = 'Rejected'
                        bid.save()

                        return JsonResponse(status=rest_framework.status.HTTP_200_OK, data=BidsSerializer(bid).data)
                    approved_count = BidDecision.objects.filter(decision='Approved', bid__tenderId=tender).count()
                    responsible_employee_count = organization.get_responsible_count()
                    if (responsible_employee_count <= 3):
                        if approved_count == responsible_employee_count:
                            tender.status = 'Closed'
                            tender.save()
                            bid.status = 'Approved'
                            bid.save()
                            return JsonResponse(status=rest_framework.status.HTTP_200_OK, data=BidsSerializer(bid).data)
                        else:
                            return JsonResponse(status=rest_framework.status.HTTP_200_OK, data=BidsSerializer(bid).data)
                    elif approved_count == 3:
                        tender.status = 'Closed'
                        tender.save()
                        bid.status = 'Approved'
                        bid.save()

                        return JsonResponse(status=rest_framework.status.HTTP_200_OK, data=BidsSerializer(bid).data)
                    else:
                        return JsonResponse(status=rest_framework.status.HTTP_200_OK, data=BidsSerializer(bid).data)

                    return JsonResponse(status=rest_framework.status.HTTP_200_OK, data=BidsSerializer(bid).data)
                else:
                    return JsonResponse(status=rest_framework.status.HTTP_403_FORBIDDEN,
                                        data={'reason': 'You are not allowed to do this'})
            else:
                return JsonResponse(status=rest_framework.status.HTTP_400_BAD_REQUEST,
                                    data={
                                        'reason': 'You can not do this, please send username as parameter'})
        except Exception as e:
            return JsonResponse(status=rest_framework.status.HTTP_400_BAD_REQUEST, data={'reason': str(e)})
