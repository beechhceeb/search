# Terraform provider configurations live here
# https://developer.hashicorp.com/terraform/language/providers
# Providers are binary supplementary modules to terraform,
# they are the interface between a cloud provider and the terraform code
# the configuration here sets up authentication and terraform state backends
terraform {
  required_version = ">= 1.6.1"
  required_providers {

    # Google providers required to build resources in GCP
    google = {
      source  = "hashicorp/google"
      version = ">= 6.13.0"
    }

    # cloudflare provider used to create DNS records for the environment
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~>4.0"
    }

  }

  # Terraform backends define a persistent store to contain the current state of built resources
  # https://developer.hashicorp.com/terraform/language/settings/backends/configuration
  # we use GCS buckets for this, a folder is created in gcs.bucket by the name gcs.prefix
  backend "gcs" {
    bucket = "mpb-terraform-state"
    prefix = "system-albatross/10-main"
  }
}

# MPB-Internal module that contains all of our trusted IPs, used to configure ingress on the load balancer.
module "ip_whitelisting" {
  #checkov:skip=CKV_TF_1: "Ensure Terraform module sources use a commit hash"
  #checkov:skip=CKV_TF_2: "Ensure Terraform module sources use a tag with a version number"
  source = "git@github.com:mpb-com/module-ip-whitelisting?ref=v1.0.24"
}

# This block provides a data source exposing the contents of terraform state for this project's instance of gcp-project-bootstrap
# https://developer.hashicorp.com/terraform/language/data-sources
# MPB's terraform patterns dictate that this project's workspace aligns with a workspace of the same name in gcp-project-bootstrap,
# thus all terraform projects in MPB must have a unique identifier for their workspace
# https://developer.hashicorp.com/terraform/language/state/workspaces
# We will use outputs (e.g. project ID) from this state backend to configure our own project.
# https://developer.hashicorp.com/terraform/language/values/outputs
data "terraform_remote_state" "project" {
  backend   = "gcs"
  workspace = terraform.workspace

  config = {
    bucket = "mpb-terraform-state"
    prefix = "gcp-project-bootstrap"
  }
}

# This block provides a data source exposing the contents of terraform state for the internal-services-prod bootstrap environment.
# We use the project ID output from this environment to configure pull permissions for the artifact registry.
data "terraform_remote_state" "internal_services_project_prod" {
  backend   = "gcs"
  workspace = "internal-services-prod"

  config = {
    bucket = "mpb-terraform-state"
    prefix = "gcp-project-bootstrap"
  }
}

# This secret contains the cloudflare API token.
# we will use this to create certificate validation DNS records when configuring lets encrypt in module-simple-cloudrun
# and to configure the cloudflare provider to create a DNS record for the environment
data "google_secret_manager_secret_version" "terraform_cloudflare" {
  project = "global-state-prod"
  secret  = "cloudflare-api-token"
}

provider "cloudflare" {
  api_token = data.google_secret_manager_secret_version.terraform_cloudflare.secret_data
}

# This block provides a data source exposing the contents of the current workspace. This is used
# As a trick to treat terraform state as a key/value store. When the var.albatross_version is updated, this is reflected back to state
data "terraform_remote_state" "self" {
  backend   = "gcs"
  workspace = terraform.workspace

  config = {
    bucket = "mpb-terraform-state"
    prefix = "system-albatross/10-main"
  }

  defaults = {
    albatross_version = "0.0.1"
  }
}

# This block provides a data source exposing the contents of terraform state for this project's 5-network stage
data "terraform_remote_state" "network" {
  backend   = "gcs"
  workspace = terraform.workspace

  config = {
    bucket = "mpb-terraform-state"
    prefix = "system-albatross/5-network"
  }
}