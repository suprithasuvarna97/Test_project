from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Item
from .serializers import ItemSerializer
from django.http import Http404
from django.core.cache import cache  # Add this for Redis caching
from django.conf import settings  # For cache TTL (timeout)
from django.http import HttpResponse
#from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from .serializers import UserSerializer
from rest_framework import generics, status

CACHE_TTL = getattr(settings, 'CACHE_TTL', 60 * 15)  # 15 minutes cache timeout


def api_root(request):
    return HttpResponse("Welcome to the Inventory API. Use /api/items/ to manage inventory.")

#class SecureEndpoint(APIView):
   # permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "You have access to this secure endpoint."})

class ItemList(APIView):
    """
    List all items, or create a new item.
    """
    #permission_classes = [IsAuthenticated]
    def get(self, request):
        items = Item.objects.all()
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ItemDetail(APIView):
    """
    Retrieve, update, or delete an item.
    """
    #permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        # Implement Redis caching
        cache_key = f'item_{pk}'
        item = cache.get(cache_key)  # Check if item is in cache

        if not item:
            item = self.get_object(pk)
            serializer = ItemSerializer(item)
            # Store in cache
            cache.set(cache_key, serializer.data, timeout=CACHE_TTL)
        else:
            # If cached, return the cached item
            return Response(item, status=status.HTTP_200_OK)

        return Response(serializer.data)

    def put(self, request, pk):
        item = self.get_object(pk)
        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Invalidate the cache after updating the item
            cache_key = f'item_{pk}'
            cache.delete(cache_key)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        item = self.get_object(pk)
        item.delete()
        # Invalidate the cache after deleting the item
        cache_key = f'item_{pk}'
        cache.delete(cache_key)
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer

class UserLoginView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user:
            token = AccessToken.for_user(user)
            return Response({'access': str(token)}, status=status.HTTP_200_OK)
        
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        
