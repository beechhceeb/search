locals {
  albatross_version_to_deploy = var.albatross_version == null ? data.terraform_remote_state.self.outputs.albatross_version : var.albatross_version
  ip_whitelist = distinct(sort(concat(
    module.ip_whitelisting.gcp_uptime_check_ips,
    module.ip_whitelisting.location_ips,
    var.external_allow_list
  )))
}