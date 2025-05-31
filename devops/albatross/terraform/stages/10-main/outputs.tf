output "dns_record_names" {
  description = "The DNS record names used for this environment."
  value       = module.simple_cloudrun.dns_record_names
}

output "albatross_version" {
  description = "The version of albatross deployed to this environment"
  value       = local.albatross_version_to_deploy
}