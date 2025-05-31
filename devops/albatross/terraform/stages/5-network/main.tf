module "network" {
  #checkov:skip=CKV_TF_1: "Ensure Terraform module sources use a commit hash"
  #checkov:skip=CKV_TF_2: "Ensure Terraform module sources use a tag with a version number"
  source           = "git@github.com:mpb-com/module-networking.git?ref=v1.0.6"
  cloudsql_enabled = false

  project_id    = data.terraform_remote_state.project.outputs.project_id
  network_name  = var.network_name
  subnet_region = var.region

  subnets = [{
    subnet_name   = "${var.network_name}-subnet"
    subnet_ip     = var.primary_subnet
    subnet_region = var.region
  }]
}