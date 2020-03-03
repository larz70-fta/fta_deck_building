from django.shortcuts import render

from slack_utils.decorators import slack_view
from django.http import HttpResponse

# Create your views here.
#from rest_framework.response import Response
#from rest_framework.decorators import api_view
#from rest_framework import status

from build_finder.models import Deck
#from .serializers import *

@slack_view
def find_deck(request, *args, **kwargs):
    # add logic here
    return HttpResponse("Hello")

#@api_view(['GET', 'POST'])
#def find_deck(request):
    # if request.method == 'GET':
    #     data = Student.objects.all()

    #     serializer = StudentSerializer(data, context={'request': request}, many=True)

    #     return Response(serializer.data)

#    if request.method == 'POST':
#        deck_name = request.POST.get('text')
        # add logic here to get the image for the deck name
        #if serializer.is_valid():
        #    serializer.save()
#        return Response(data="{ 'text': 'You are searching for deck_name: " + deck_name + "' }")
#    else:        
#        return Response(data="SWW", status=status.HTTP_400_BAD_REQUEST)

# @api_view(['PUT', 'DELETE'])
# def students_detail(request, pk):
#     try:
#         student = Student.objects.get(pk=pk)
#     except Student.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)

#     if request.method == 'PUT':
#         serializer = StudentSerializer(student, data=request.data,context={'request': request})
#         if serializer.is_valid():
#             serializer.save()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     elif request.method == 'DELETE':
#         student.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
