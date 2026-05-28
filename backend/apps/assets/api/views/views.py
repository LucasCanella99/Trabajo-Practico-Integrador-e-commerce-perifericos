from rest_framework import viewsets
from apps.assets.models import SiteAsset
from apps.assets.api.serializers import SiteAssetSerializer

class SiteAssetViewSet(viewsets.ModelViewSet):
    queryset = SiteAsset.objects.all()
    serializer_class = SiteAssetSerializer