resource "aws_lambda_event_source_mapping" "main" {
  event_source_arn  = aws_dynamodb_table.this.stream_arn
  function_name     = aws_lambda_function.to_s3.arn
  starting_position = "LATEST"
  batch_size = 400
}


data "archive_file" "tos3" {
  type        = "zip"
  source_file = "functions/lambdatos3.py"
  output_path = "functions/package.zip"
}


resource "aws_lambda_function" "to_s3" {
  # If the file is not in the current working directory you will need to include a
  # path.module in the filename.
  function_name = "lambda_function_tos3"
  role          = aws_iam_role.streaming.arn
  filename = "${path.module}/functions/lambdatos3.zip"
  lifecycle {
    ignore_changes = [filename]
  }
  runtime = "python3.8"
  handler = "lambdatos3.lambda_handler"

  environment {
    variables = {
      BUCKET_NAME    = aws_s3_bucket.tos3.bucket
    }
  }
}