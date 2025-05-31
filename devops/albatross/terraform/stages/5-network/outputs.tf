output "nat_gateway_external_ip_address" {
  description = "Static IP of the nat gateway"
  value       = module.network.nat_gateway_external_ip_address
}

output "cloudrun_vpc_config" {
    description = "The VPC config required by cloudrun"
    value = {
        network = module.network.network_name
        subnetwork = module.network.subnets_names[0]
    }
}