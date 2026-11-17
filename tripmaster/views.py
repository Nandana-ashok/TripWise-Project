from django.shortcuts import render,get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from tripmaster.serializers import UserSerializer,TripSerializer,TripMemberSerializer
from tripmaster.models import TripDb,TripMemberDb
from rest_framework import authentication,permissions,serializers
from tripmaster.permissions import OwnerOnly
from rest_framework.exceptions import PermissionDenied
# Create your views here.

class SignUpView(APIView):

    def post(self,request):

        form_data = request.data
        serializer_instance = UserSerializer(data=form_data)

        if serializer_instance.is_valid():

            serializer_instance.save()
            return Response(data=serializer_instance.data)
        else:
            return Response(data=serializer_instance.errors)

    def get(self,request):

        qs = User.objects.all()
        serializer = UserSerializer(qs,many=True)
        return Response(data = serializer.data)

class UserRetrieveUpdateDeleteView(APIView):    
    
    def delete(self,request,pk):

        qs = get_object_or_404(User,id=pk)
        qs.delete()
        return Response({"Message":"User deleted successfully..."})



class TripListCreateView(APIView):
    
    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self,request):

        qs = TripDb.objects.filter(created_by=request.user)
        serializer = TripSerializer(qs,many=True)
        return Response(data=serializer.data)

    def post(self,request):

        form_data = request.data
        serializer_instance = TripSerializer(data=form_data)
        if serializer_instance.is_valid():
            serializer_instance.save(created_by=request.user)
            return Response(data=
                            {
                                "Message" : "Trip created successfully",
                                "Your Trip Details": serializer_instance.data
                            })
        else:
            return Response(data=serializer_instance.errors)

class TripRetrieveUpdateDeleteView(APIView):

    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [OwnerOnly]

    def get(self,request,pk):

        trip_object = get_object_or_404(TripDb,id=pk)
        if trip_object.created_by == request.user :
            serializer_instance = TripSerializer(trip_object)
            return Response(data=serializer_instance.data)
        else:
            raise serializers.ValidationError("Access Denied.....")

    def put(self,request,pk):

        trip_object = get_object_or_404(TripDb,id=pk)

        if trip_object.created_by != request.user:
            raise serializers.ValidationError("Access Denied....")
        else:
            form_data = request.data
            serializer_instance = TripSerializer(data=form_data,instance=trip_object)
            if serializer_instance.is_valid():
                serializer_instance.save()
                return Response(data={
                    "Message": "Data updated successfully....",
                    "Updated data": serializer_instance.data
                })
            else:
                return Response(data=serializer_instance.errors)

    def delete(self,request,pk):

        trip_object = get_object_or_404(TripDb,id=pk)
        if trip_object.created_by == request.user :
            trip_object.delete()
            return Response({"Message":"Data deleted successfully...."})
        raise serializers.ValidationError("Access Denied.....")


class TripMemberCreateListView(APIView):

    def get(self,request,trip_id):

        trip_object = get_object_or_404(TripDb,id=trip_id)

        is_owner = trip_object.created_by == request.user
        is_member = TripMemberDb.objects.filter(trip=trip_object,user=request.user).exists()

        if not (is_owner or is_member):
            raise PermissionDenied("You are not allowed to see this trip....")
        members = TripMemberDb.objects.filter(trip=trip_object)

        serializer_instance = TripMemberSerializer(members,many=True)
        return Response(data=serializer_instance.data)

    def post(self,request,trip_id):

        trip_object = get_object_or_404(TripDb,id=trip_id)

        if trip_object.created_by != request.user :
            raise PermissionDenied("Only owner can add members to the trip")

        form_data = request.data
        serializer_instance = TripMemberSerializer(data= form_data,context={'trip':trip_object})

        if serializer_instance.is_valid():
            serializer_instance.save()
            return Response({"Message":"Member added succeessfully....."})
        else:
            return Response(data=serializer_instance.errors)

class TripMemberDeleteView(APIView):
    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [OwnerOnly]

    def delete(self,request,trip_id,member_id):
        
        trip_object = get_object_or_404(TripDb,id=trip_id)
        if trip_object.created_by != request.user:
            raise PermissionDenied("Only trip owner has access to delete members.......")
        else:
            member_object = get_object_or_404(TripMemberDb,id=member_id,trip=trip_object)
            member_object.delete()
            return Response({"Message":"Member deleted successfully...."})