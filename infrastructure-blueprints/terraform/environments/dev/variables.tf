variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "ecr_repo_url" {
  type = string
}

variable "image_tag" {
  type    = string
  default = "latest"
}

variable "execution_role_arn" {
  type = string
}

variable "task_role_arn" {
  type = string
}

variable "ecs_cluster_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "service_sg_id" {
  type = string
}

variable "blackwall_target_group_arn" {
  type = string
}

variable "anthropic_api_key_arn" {
  type = string
}

variable "log_group_name" {
  type = string
}
