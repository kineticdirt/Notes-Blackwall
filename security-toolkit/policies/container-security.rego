package container_security

default allow = false

allow {
    not runs_as_root
    has_resource_limits
    has_health_check
}

runs_as_root {
    input.spec.containers[_].securityContext.runAsUser == 0
}

runs_as_root {
    not input.spec.containers[_].securityContext.runAsNonRoot
}

has_resource_limits {
    input.spec.containers[_].resources.limits.cpu
    input.spec.containers[_].resources.limits.memory
}

has_health_check {
    input.spec.containers[_].livenessProbe
    input.spec.containers[_].readinessProbe
}

violation[msg] {
    runs_as_root
    msg := "Container must not run as root"
}

violation[msg] {
    not has_resource_limits
    msg := "Container must have CPU and memory limits"
}

violation[msg] {
    not has_health_check
    msg := "Container must have liveness and readiness probes"
}
