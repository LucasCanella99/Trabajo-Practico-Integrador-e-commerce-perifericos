from rest_framework import serializers
from apps.assets.models import SiteAsset

class SiteAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteAsset
        fields = '__all__'