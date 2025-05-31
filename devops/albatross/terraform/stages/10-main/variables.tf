# Terraform variables live here
# https://developer.hashicorp.com/terraform/language/values/variables
# these variables are used to configure resources defined in this terraform project
variable "region" {
  type        = string
  description = "The region in which to provision the resources of this system"
  default     = "europe-west1"
}

variable "albatross_registry" {
  type        = string
  description = "The registry where the container image is pulled from"
  default     = "europe-west1-docker.pkg.dev/internal-services-prod-453c/mpb-docker/albatross"
}

variable "albatross_version" {
  type        = string
  description = "The version of albatross image to deploy"
  default     = null
}

variable "base_subdomains" {
  type        = list(string)
  description = "The subdomain base used for this environment. Will be pre-pended to mpb.com"
  default     = ["albatross.internal-services"]
}

variable "mpb_platform_address" {
  type        = string
  description = "The address of the environment for albatross to connect to. The environment must have var.albatross_ingress_enabled set to true"
  default     = "www.staging.env.mpb.com"
}

variable "external_allow_list" {
  type        = list(string)
  description = "List of cidr-annotated addresses to allow access to albatross, in addition to the addresses passed in by the whitelisting module."
  default     = []
}

variable "min_scale" {
  type        = number
  description = "Minimum number of containers to scale to"
  default     = 0
}