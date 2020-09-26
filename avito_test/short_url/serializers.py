from avito_test.short_url.models import ShortLink
from rest_framework.renderers import serializers


class ShortLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortLink
        fields = ['old_link', 'new_link', 'created']
