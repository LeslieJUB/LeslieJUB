provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project = var.project_name
      Environment = var.environment
      ManagedBy = "Terraform"
    }
  }
}

data "aws_caller_identity" "current" {}

resource "aws_kms_key" "lake" {
  description = "Encryption key for ${var.project_name} ${var.environment} data lake"
  deletion_window_in_days = 7
  enable_key_rotation = true
}

resource "aws_kms_alias" "lake" {
  name = "alias/${var.project_name}-${var.environment}-lake"
  target_key_id = aws_kms_key.lake.key_id
}

locals { zones = toset(["bronze", "silver", "gold"]) }

resource "aws_s3_bucket" "lake" {
  for_each = local.zones
  bucket = "${var.project_name}-${var.environment}-${each.key}-${data.aws_caller_identity.current.account_id}"
  force_destroy = var.force_destroy
}

resource "aws_s3_bucket_versioning" "lake" {
  for_each = aws_s3_bucket.lake
  bucket = each.value.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "lake" {
  for_each = aws_s3_bucket.lake
  bucket = each.value.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
      kms_master_key_id = aws_kms_key.lake.arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "lake" {
  for_each = aws_s3_bucket.lake
  bucket = each.value.id
  block_public_acls = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "lake" {
  for_each = aws_s3_bucket.lake
  bucket = each.value.id
  rule {
    id = "expire-noncurrent-versions"
    status = "Enabled"
    filter {}
    noncurrent_version_expiration { noncurrent_days = 90 }
  }
}
