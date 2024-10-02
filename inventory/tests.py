from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Item

class ItemTests(APITestCase):

    def test_create_item(self):
        url = reverse('item-list')  # Assuming the URL pattern name is 'item-list'
        data = {'name': 'Laptop', 'description': 'High-performance laptop', 'quantity': 10}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_read_item(self):
        item = Item.objects.create(name='Laptop', description='High-performance laptop', quantity=10)
        url = reverse('item-detail', args=[item.id])  # Assuming 'item-detail' URL
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'], 10)  # Checking quantity is returned correctly

    def test_update_item(self):
        item = Item.objects.create(name='Laptop', description='High-performance laptop', quantity=10)
        url = reverse('item-detail', args=[item.id])
        data = {'name': 'Laptop', 'description': 'Updated description', 'quantity': 15}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'], 15)  # Checking the updated quantity

    def test_delete_item(self):
        item = Item.objects.create(name='Laptop', description='High-performance laptop', quantity=10)
        url = reverse('item-detail', args=[item.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
