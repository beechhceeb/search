# Terraform resources live here
# https://developer.hashicorp.com/terraform/language/resources
# we will define resources here directly
# or call modules of terraform code to build resources in the cloud

module "simple_cloudrun" {
  #checkov:skip=CKV_TF_1: "Ensure Terraform module sources use a commit hash"
  #checkov:skip=CKV_TF_2: Ensure "Terraform module sources use a tag with a version number"
  source                       = "git@github.com:mpb-com/module-simple-cloudrun?ref=v1.1.2"
  region                       = var.region
  project_id                   = data.terraform_remote_state.project.outputs.project_id
  internal_services_project_id = data.terraform_remote_state.internal_services_project_prod.outputs.project_id
  container_registry           = var.albatross_registry
  container_version            = local.albatross_version_to_deploy
  name                         = "albatross"
  ip_whitelist                 = local.ip_whitelist
  base_subdomains              = var.base_subdomains
  min_scale                    = var.min_scale
  env_vars = {
    GOOGLE_CLOUD_PROJECT      = data.terraform_remote_state.project.outputs.project_id
    GOOGLE_CLOUD_LOCATION     = "us-central1"
    GOOGLE_GENAI_USE_VERTEXAI = "True"
    LLM_ENABLED               = "true"
    SEARCH_PROXY_URL          = "https://${var.mpb_platform_address}/search-service/product/query/"
  }
  direct_vpc_egress_config = {
    enabled    = true
    network    = data.terraform_remote_state.network.outputs.cloudrun_vpc_config.network
    subnetwork = data.terraform_remote_state.network.outputs.cloudrun_vpc_config.subnetwork
    egress     = "ALL_TRAFFIC"
    tags       = []
  }
}

resource "google_project_iam_member" "aiplatform" {
  project = data.terraform_remote_state.project.outputs.project_id
  member  = module.simple_cloudrun.cloudrun_service_account.member
  # TODO: Once we have decided which API interfaces we are going to use, reduce this to a better role than admin
  role = "roles/aiplatform.user"
}
