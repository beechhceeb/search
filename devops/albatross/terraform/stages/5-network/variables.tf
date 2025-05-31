variable "network_name" {
  type        = string
  description = "Name of the project VPC"
  default     = "albatross-vpc"
}

variable "primary_subnet" {
  description = "CIDR range of the VPC."
  default     = "10.33.0.0/24"
  type        = string
}

variable "region" {
  type        = string
  description = "The region in which to provision the resources of this system"
  default     = "europe-west1"
}