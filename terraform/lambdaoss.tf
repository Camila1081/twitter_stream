resource "aws_lambda_layer_version" "layer" {
  filename             = data.archive_file.layer.output_path
  source_code_hash    = data.archive_file.layer.output_base64sha256
  layer_name          = "layer"
  compatible_runtimes = ["python3.8"]
}

data "archive_file" "layer" {
  type        = "zip"
  source_dir  = "${path.module}/functions/package"
  output_path = "${path.module}/functions/package.zip"
}

data "aws_dynamodb_table" "table" {
  name     = aws_dynamodb_table.this.name
}
resource "aws_lambda_function" "streaming" {
  function_name    = "streaming-${aws_dynamodb_table.this.name}"
  role             = aws_iam_role.streaming.arn
  runtime          = "python3.8"
  filename          = data.archive_file.streaming.output_path
  source_code_hash = data.archive_file.streaming.output_base64sha256
  layers           = [aws_lambda_layer_version.layer.arn]
  timeout          = 60
  handler         ="${aws_dynamodb_table.this.name}.handler"
  environment {
    variables = {
      ENDPOINT = aws_opensearch_domain.main.endpoint
      INDEX    = aws_dynamodb_table.this.name
    }
  }

}
data "archive_file" "streaming" {
  type        = "zip"
  source_file = "functions/${aws_dynamodb_table.this.name}.py"
  output_path = "functions/${aws_dynamodb_table.this.name}.zip"
}

resource "aws_lambda_event_source_mapping" "stream_mapping" {
  batch_size        = 100
  event_source_arn  = data.aws_dynamodb_table.table.stream_arn
  function_name     = aws_lambda_function.streaming.arn
  starting_position = "LATEST"
  depends_on        = [aws_iam_role.streaming]
}
