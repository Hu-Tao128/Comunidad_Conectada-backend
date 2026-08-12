"""Serializer reutilizable para gestionar galerías de imágenes."""

from rest_framework import serializers

from apps.galeria.models import GaleriaImagen


class GaleriaSerializerMixin:
    """Añade lectura/escritura de la galería de imágenes a un serializer.

    Los serializers que lo hereden deben definir ``GALERIA_FK`` con el nombre
    del campo FK del modelo ``GaleriaImagen`` que apunta a su entidad.
    """

    GALERIA_FK = ""

    galeria = serializers.SerializerMethodField()
    galeria_archivos = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
    )
    galeria_eliminar = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
    )

    def get_galeria(self, obj):
        return [
            {"id": str(imagen.id), "url": imagen.archivo.url}
            for imagen in obj.galeria.all()
        ]

    def _aplicar_galeria(self, obj, archivos, eliminar):
        if eliminar:
            obj.galeria.filter(id__in=eliminar).delete()

        if archivos:
            user = (
                self.context.get("request").user
                if self.context.get("request")
                else None
            )
            for orden, archivo in enumerate(archivos):
                GaleriaImagen.objects.create(
                    **{self.GALERIA_FK: obj},
                    archivo=archivo,
                    orden=orden,
                    created_by=user,
                    updated_by=user,
                )

    def create(self, validated_data):
        archivos = validated_data.pop("galeria_archivos", None)
        eliminar = validated_data.pop("galeria_eliminar", None)
        obj = super().create(validated_data)
        self._aplicar_galeria(obj, archivos, eliminar)
        return obj

    def update(self, instance, validated_data):
        archivos = validated_data.pop("galeria_archivos", None)
        eliminar = validated_data.pop("galeria_eliminar", None)
        obj = super().update(instance, validated_data)
        self._aplicar_galeria(obj, archivos, eliminar)
        return obj
