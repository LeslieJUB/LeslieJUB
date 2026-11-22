variable "aws_region" {
  description = "AWS region for StreamForge resources."
  type = string
  default = "eu-central-1"
}
variable "project_name" {
  type = string
  default = "streamforge"
}
variable "environment" {
  type = string
  default = "dev"
}
variable "force_destroy" {
  description = "Allow Terraform to delete non-empty buckets. Keep false for safer environments."
  type = bool
  default = false
}
