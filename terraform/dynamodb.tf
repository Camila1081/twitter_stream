resource "aws_dynamodb_table" "this" {
  name         = "${var.environment}_table"
  billing_mode = "PAY_PER_REQUEST"
  stream_enabled   = true
  stream_view_type = "NEW_IMAGE"
  table_class  = "STANDARD"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = var.tags
}