HA_MODE_HOT_STANDBY = "hot-standby"
HA_MODE_LOAD_BALANCING = "load-balancing"
HA_MODE_STANDALONE = "standalone"

HA_MODE_CHOICES = (
    (HA_MODE_HOT_STANDBY, "Hot standby"),
    (HA_MODE_LOAD_BALANCING, "Load balancing"),
    (HA_MODE_STANDALONE, "Standalone"),
)

FAMILY_IPV4 = "ipv4"
FAMILY_IPV6 = "ipv6"
FAMILY_BOTH = "both"

FAMILY_CHOICES = (
    (FAMILY_IPV4, "IPv4"),
    (FAMILY_IPV6, "IPv6"),
    (FAMILY_BOTH, "Both"),
)

JOB_PENDING = "pending"
JOB_RUNNING = "running"
JOB_SUCCESS = "success"
JOB_PARTIAL = "partial"
JOB_FAILED = "failed"

JOB_STATUS_CHOICES = (
    (JOB_PENDING, "Pending"),
    (JOB_RUNNING, "Running"),
    (JOB_SUCCESS, "Success"),
    (JOB_PARTIAL, "Partial"),
    (JOB_FAILED, "Failed"),
)
