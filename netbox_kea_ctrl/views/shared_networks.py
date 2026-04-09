class KeaSharedNetworkRemovePrefixView(View):
    def post(self, request, pk, prefix_id):
        obj = get_object_or_404(KeaSharedNetwork, pk=pk)
        prefix = get_object_or_404(Prefix, pk=prefix_id)

        targets = list(obj.get_publish_targets())
        if not targets:
            messages.error(request, "No publish targets resolved for this Shared Network.")
            return redirect("plugins:netbox_kea_ctrl:keasharednetwork", pk=obj.pk)

        target = targets[0]

        from netbox_kea_ctrl.models import KeaPrefixPool
        pools = list(KeaPrefixPool.objects.filter(prefix=prefix))

        job = KeaPublishJob.objects.create(
            created_by=request.user,
            server_tag_name=obj.server_tag.name if obj.server_tag else "",
            status="running",
            summary=f"Remove Prefix '{prefix.prefix}' from Shared Network '{obj.name}'",
            validation_output={
                "shared_network": obj.name,
                "prefix": str(prefix.prefix),
                "selected_target": target.name,
                "resolved_targets": [server.name for server in targets],
                "pool_count": len(pools),
                "pools": [pool.pool_string for pool in pools],
            },
        )

        try:
            from netbox_kea_ctrl.services.subnet_remover import SubnetRemover

            remover = SubnetRemover()
            outcome = remover.remove(obj, prefix, target)

            job.generated_payload = outcome["payload"]
            job.publish_output = outcome["result"]

            kea_ok = False
            kea_errors = []

            result = outcome["result"]
            if isinstance(result, list) and result:
                kea_ok = all(item.get("result") == 0 for item in result)
                kea_errors = [item.get("text", "") for item in result if item.get("result") != 0]
            elif isinstance(result, dict):
                kea_ok = result.get("result") == 0
                if not kea_ok:
                    kea_errors = [result.get("text", "Unknown Kea error")]
            else:
                kea_errors = ["Unexpected Kea response format"]

            if kea_ok:
                # 1. Delete all pools for this prefix
                deleted_pool_count = len(pools)
                for pool in pools:
                    pool.delete()

                # 2. Remove shared network assignment on prefix
                service = PrefixAssignmentService()
                service.remove_prefix_from_shared_network(prefix, obj)

                job.status = "success"
                job.validation_output = {
                    **(job.validation_output or {}),
                    "deleted_pool_count": deleted_pool_count,
                }
                messages.success(
                    request,
                    f"Prefix {prefix.prefix} removed from Shared Network '{obj.name}', deleted from Kea, and {deleted_pool_count} pool(s) were removed from NetBox."
                )
            else:
                job.status = "failed"
                job.error_log = "\n".join(filter(None, kea_errors))
                messages.error(
                    request,
                    f"Prefix removal failed in Kea: {job.error_log or 'Kea returned an error'}"
                )

            job.save()

        except Exception as exc:
            job.status = "failed"
            job.error_log = str(exc)
            job.save()
            messages.error(request, f"Prefix removal failed: {exc}")

        return redirect("plugins:netbox_kea_ctrl:keapublishjob", pk=job.pk)
