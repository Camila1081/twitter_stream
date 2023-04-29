output "aws_region" {
  value = var.aws_region
}

output "dynamo_table_name" {
  value = aws_dynamodb_table.this.name
}

output "kinesis_stream_name" {
  value = aws_kinesis_stream.this.name
}