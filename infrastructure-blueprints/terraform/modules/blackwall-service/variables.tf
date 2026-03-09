variable "project" {
  type    = string
  default = "cequence"
}

variable "environment" {
  type = string
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "cpu" {
  type    = number
  default = 512
}

variable "memory" {
  type    = number
  default = 1024
}

variable "desired_count" {
  type    = number
  default = 2
}

variable "ecr_repo_url" {
  type = string
}

variable "image_tag" {
  type    = string
  default = "latest"
}

variable "log_level" {
  type    = string
  default = "info"
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

variable "target_group_arn" {
  type = string
}

variable "anthropic_api_key_arn" {
  type        = string
  description = "ARN of the Secrets Manager secret for Anthropic API key"
}

variable "log_group_name" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}
