output "data_lake_buckets" {
  description = "S3 bucket names for bronze, silver and gold zones."
  value = { for zone, bucket in aws_s3_bucket.lake : zone => bucket.bucket }
}
output "kms_key_arn" {
  value = aws_kms_key.lake.arn
  description = "KMS key used for S3 server-side encryption."
}
