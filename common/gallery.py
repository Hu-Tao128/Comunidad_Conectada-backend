from rest_framework import serializers


def validar_imagen(archivo, field_name="galeria_archivos"):
    if archivo.size > 8 * 1024 * 1024:
        raise serializers.ValidationError({field_name: "La imagen no puede superar 8 MB."})
    content_type = getattr(archivo, "content_type", "")
    if content_type and content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise serializers.ValidationError({field_name: "Solo se permiten imágenes JPG, PNG o WEBP."})


def sincronizar_galeria(instance, *, related_name, model, parent_field, files, removed_ids, user, field_name="imagen"):
    gallery = getattr(instance, related_name)
    if removed_ids:
        gallery.filter(id__in=removed_ids).delete()
    for archivo in files:
        validar_imagen(archivo)
        model.objects.create(**{
            parent_field: instance,
            field_name: archivo,
            "created_by": user,
            "updated_by": user,
        })
