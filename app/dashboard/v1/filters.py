import django_filters

from app.creator.models import CreatorApplication


class CreatorApplicationFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(
        field_name="status"
    )

    class Meta:
        model = CreatorApplication
        fields = ["status"]
