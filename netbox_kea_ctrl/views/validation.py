from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView

from netbox_kea_ctrl.models import KeaPublishJob, KeaServerTag, KeaSharedNetwork
from netbox_kea_ctrl.services.config_builder import KeaConfigBuilder
from netbox_kea_ctrl.services.loader import PrefixLoader
from netbox_kea_ctrl.services.validator import PrefixValidator


class PrefixValidationView(TemplateView):
    template_name = "netbox_kea_ctrl/prefix_validation.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        loader = PrefixLoader()
        prefixes = loader.load()

        server_tags = list(KeaServerTag.objects.filter(enabled=True))
        shared_networks = list(KeaSharedNetwork.objects.filter(enabled=True).select_related("server_tag"))

        validator = PrefixValidator(server_tags, shared_networks)
        validated = [validator.validate(mp) for mp in prefixes]

        context["validated_prefixes"] = validated
        context["server_tags"] = server_tags
        return context


class PreviewServerTagView(View):
    def get(self, request, server_tag):
        loader = PrefixLoader()
        prefixes = loader.load()

        server_tags = list(KeaServerTag.objects.filter(enabled=True))
        shared_networks = list(KeaSharedNetwork.objects.filter(enabled=True).select_related("server_tag"))

        validator = PrefixValidator(server_tags, shared_networks)
        validated = [validator.validate(mp) for mp in prefixes]

        builder = KeaConfigBuilder()
        payload = builder.build_for_server_tag(validated, server_tag)

        return JsonResponse(payload, safe=False)


class PublishServerTagView(View):
    def post(self, request, server_tag):
        server_tag_obj = get_object_or_404(KeaServerTag, name=server_tag, enabled=True)

        loader = PrefixLoader()
        prefixes = loader.load()

        server_tags = list(KeaServerTag.objects.filter(enabled=True))
        shared_networks = list(KeaSharedNetwork.objects.filter(enabled=True).select_related("server_tag"))

        validator = PrefixValidator(server_tags, shared_networks)
        validated = [validator.validate(mp) for mp in prefixes]

        builder = KeaConfigBuilder()
        payload = builder.build_for_server_tag(validated, server_tag)

        job = KeaPublishJob.objects.create(
            created_by=request.user,
            server_tag_name=server_tag,
            status="success",
            validation_output={
                "prefixes": [
                    {
                        "prefix": mp.prefix,
                        "state": mp.validation_state,
                        "messages": mp.messages,
                    }
                    for mp in validated
                    if mp.kea_server_tag == server_tag
                ]
            },
            generated_payload=payload,
            publish_output={"status": "dry-run-placeholder"},
        )

        return redirect("plugins:netbox_kea_ctrl:keapublishjob", pk=job.pk)
