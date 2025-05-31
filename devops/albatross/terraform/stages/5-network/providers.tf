terraform {
  required_version = ">= 1.6.6"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 6.33.0"
    }

    random = {
      source  = "hashicorp/random"
      version = "3.6.2"
    }

    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "4.35.0"
    }

  }

  backend "gcs" {
    bucket = "mpb-terraform-state"
    prefix = "system-albatross/5-network"
  }
}

data "terraform_remote_state" "project" {
  backend   = "gcs"
  workspace = terraform.workspace

  config = {
    bucket = "mpb-terraform-state"
    prefix = "gcp-project-bootstrap"
  }
}

module "ip_whitelisting" {
  #checkov:skip=CKV_TF_1: "Ensure Terraform module sources use a commit hash"
  #checkov:skip=CKV_TF_2: "Ensure Terraform module sources use a tag with a version number"
  source = "git@github.com:mpb-com/module-ip-whitelisting?ref=v1.0.24"
}

data "google_secret_manager_secret_version" "cloudflare_api_token" {
  project = "global-state-prod"
  secret  = "cloudflare-api-token"
}

provider "cloudflare" {
  api_token = data.google_secret_manager_secret_version.cloudflare_api_token.secret_data
}