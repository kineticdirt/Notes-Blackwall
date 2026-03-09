terraform {
  required_version = ">= 1.5"

  backend "s3" {
    bucket         = "cequence-terraform-state"
    key            = "dev/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "cequence-blackwall"
      Environment = "dev"
      ManagedBy   = "terraform"
    }
  }
}

locals {
  environment = "dev"
  project     = "cequence"
}

module "blackwall" {
  source = "../../modules/blackwall-service"

  project               = local.project
  environment           = local.environment
  ecr_repo_url          = var.ecr_repo_url
  image_tag             = var.image_tag
  execution_role_arn    = var.execution_role_arn
  task_role_arn         = var.task_role_arn
  ecs_cluster_id        = var.ecs_cluster_id
  private_subnet_ids    = var.private_subnet_ids
  service_sg_id         = var.service_sg_id
  target_group_arn      = var.blackwall_target_group_arn
  anthropic_api_key_arn = var.anthropic_api_key_arn
  log_group_name        = var.log_group_name
  desired_count         = 1
  cpu                   = 256
  memory                = 512

  tags = {
    Service = "blackwall"
  }
}
