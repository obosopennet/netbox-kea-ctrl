class KeaSharedNetworkPushAllPrefixesView(View):
    def post(self, request, pk):
        obj = get_object_or_404(KeaSharedNetwork, pk=pk)

        targets = list(obj.get_publish_targets())
        if not targets:
            messages.error(request, "No publish targets resolved for this Shared Network.")
            return redirect("plugins:netbox_kea_ctrl:keasharednetwork", pk=obj.pk)

        target = targets[0]

        service = PrefixAssignmentService()
        prefixes = service.get_prefixes_for_shared_network(obj)

        if not prefixes:
            messages.warning(request, "No assigned active managed prefixes found for this Shared Network.")
            return redirect("plugins:netbox_kea_ctrl:keasharednetwork", pk=obj.pk)

        job = KeaPublishJob.objects.create(
            created_by=request.user,
            server_tag_name=obj.server_tag.name if obj.server_tag else "",
            status="running",
            summary=f"Push all Prefixes for Shared Network '{obj.name}'",
            validation_output={
                "shared_network": obj.name,
                "selected_target": target.name,
                "resolved_targets": [server.name for server in targets],
                "prefixes": [str(prefix.prefix) for prefix in prefixes],
            },
        )

        from netbox_kea_ctrl.services.subnet_publisher import SubnetPublisher

        publisher = SubnetPublisher()
        outputs = []
        errors = []

        for prefix in prefixes:
            try:
                outcome = publisher.push(obj, prefix, target)
                outputs.append({
                    "prefix": str(prefix.prefix),
                    "result": outcome["result"],
                    "payload": outcome["payload"],
                })

                result = outcome["result"]
                if isinstance(result, list) and result:
                    for item in result:
                        if item.get("result") != 0:
                            errors.append(f"{prefix.prefix}: {item.get('text', 'Unknown error')}")
                elif isinstance(result, dict):
                    if result.get("result") != 0:
                        errors.append(f"{prefix.prefix}: {result.get('text', 'Unknown error')}")
                else:
                    errors.append(f"{prefix.prefix}: Unexpected response format")

            except Exception as exc:
                errors.append(f"{prefix.prefix}: {exc}")

        job.publish_output = outputs

        if errors:
            job.status = "failed"
            job.error_log = "\n".join(errors)
            messages.error(request, f"Push all prefixes completed with errors. See job {job.pk}.")
        else:
            job.status = "success"
            messages.success(request, f"All prefixes for Shared Network '{obj.name}' pushed successfully.")

        job.save()
        return redirect("plugins:netbox_kea_ctrl:keapublishjob", pk=job.pk)
