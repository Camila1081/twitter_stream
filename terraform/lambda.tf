resource "aws_lambda_layer_version" "layer" {
  filename             = data.archive_file.layer.output_path
  source_code_hash    = data.archive_file.layer.output_base64sha256
  layer_name          = "layer"
  compatible_runtimes = ["nodejs12.x"]
}

data "archive_file" "layer" {
  type        = "zip"
  source_dir  = "${path.module}/functions/layer"
  output_path = "${path.module}/functions/layer.zip"
}

data "aws_dynamodb_table" "table" {
  for_each = toset([aws_dynamodb_table.this.name])
  name     = each.value
}
resource "aws_lambda_function" "streaming" {
  for_each         = data.aws_dynamodb_table.table
  function_name    = "streaming-${each.value.name}"
  role             = aws_iam_role.streaming.arn
  handler          = "${each.value.name}.handler"
  runtime          = "nodejs12.x"
  filename          = data.archive_file.streaming[each.value.name].output_path
  source_code_hash = data.archive_file.streaming[each.value.name].output_base64sha256
  layers           = [aws_lambda_layer_version.layer.arn]
  timeout          = 60

  environment {
    variables = {
      ENDPOINT = aws_opensearch_domain.main.endpoint
      INDEX    = each.value.name
    }
  }

}
data "archive_file" "streaming" {
  for_each    = data.aws_dynamodb_table.table
  type        = "zip"
  source_file = "functions/${each.value.name}.js"
  output_path = "functions/${each.value.name}.zip"
}

resource "aws_lambda_event_source_mapping" "stream_mapping" {
  for_each          = data.aws_dynamodb_table.table
  batch_size        = 100
  event_source_arn  = data.aws_dynamodb_table.table[each.value.name].stream_arn
  function_name     = aws_lambda_function.streaming[each.value.name].arn
  starting_position = "LATEST"
  depends_on        = [aws_iam_role.streaming]
}
