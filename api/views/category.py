from rest_framework import viewsets
from api.models import Category
from api.serializers.category import CategorySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name", "created_at", "id")
    serializer_class = CategorySerializer