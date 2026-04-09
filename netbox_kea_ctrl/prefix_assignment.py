from ipam.models import Prefix


class PrefixAssignmentService:
    MANAGED_TAG = "kea-managed"
    SHARED_NETWORK_CF = "kea_shared_network"

    def get_candidate_prefixes(self):
        """
        Prefixes that are eligible to be attached to a Shared Network:
        - active
        - tagged kea-managed
        - not containers
        """
        qs = (
            Prefix.objects.all()
            .prefetch_related("tags", "vrf")
            .order_by("prefix")
        )

        candidates = []
        for prefix in qs:
            if not self._is_active(prefix):
                continue
            if self._is_container(prefix):
                continue
            if not self._has_managed_tag(prefix):
                continue
            candidates.append(prefix)

        return candidates

    def get_prefixes_for_shared_network(self, shared_network):
        prefixes = self.get_candidate_prefixes()
        return [
            prefix
            for prefix in prefixes
            if self._get_shared_network_value(prefix) == shared_network.name
        ]

    def assign_prefix_to_shared_network(self, prefix, shared_network):
        cfd = dict(prefix.custom_field_data or {})
        cfd[self.SHARED_NETWORK_CF] = shared_network.name
        prefix.custom_field_data = cfd
        prefix.save()
        return prefix

    def remove_prefix_from_shared_network(self, prefix, shared_network):
        cfd = dict(prefix.custom_field_data or {})
        if cfd.get(self.SHARED_NETWORK_CF) == shared_network.name:
            cfd[self.SHARED_NETWORK_CF] = ""
            prefix.custom_field_data = cfd
            prefix.save()
        return prefix

    def _get_shared_network_value(self, prefix):
        return (prefix.custom_field_data or {}).get(self.SHARED_NETWORK_CF)

    def _has_managed_tag(self, prefix):
        return prefix.tags.filter(slug=self.MANAGED_TAG).exists()

    def _is_active(self, prefix):
        # NetBox status may be object or string-like depending on version/use
        status_value = getattr(prefix.status, "value", None) or str(prefix.status)
        return str(status_value).lower() == "active"

    def _is_container(self, prefix):
        # Prefer explicit field if present, otherwise infer from status/role if available
        if hasattr(prefix, "is_pool"):
            pass  # irrelevant, just future-proofing

        if hasattr(prefix, "mark_utilized"):
            pass

        # NetBox Prefix commonly has a status, but container-ness is often contextual.
        # If there is an explicit field, use it.
        if hasattr(prefix, "is_container"):
            try:
                return bool(prefix.is_container)
            except Exception:
                return False

        # Safe fallback: only include prefixes with an exact active status and leave
        # container filtering mostly to explicit metadata.
        return False
