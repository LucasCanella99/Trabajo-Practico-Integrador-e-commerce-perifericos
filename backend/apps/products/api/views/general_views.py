
from apps.base.api import GeneralListApiView
from apps.products.api.serializers.general_serializers import MeasureUnitSerializer, IndicadorSerializer, ProductCategorySerializer


class MeasureUnitListAPIVIEW(GeneralListApiView): 
    serializer_class = MeasureUnitSerializer

    
class IndicadorListAPIVIEW(GeneralListApiView): 
    serializer_class = IndicadorSerializer

    
class ProductCategoryListAPIVIEW(GeneralListApiView): 
    serializer_class = ProductCategorySerializer


