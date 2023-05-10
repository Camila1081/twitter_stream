resource "aws_iam_role" "streaming" {
  name               = "streaming_role"
  assume_role_policy = data.aws_iam_policy_document.assume.json
}
data "aws_iam_policy_document" "assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type       = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}



resource "aws_iam_policy" "access" {
  name   = "streaming_policy"
  policy = data.aws_iam_policy_document.access.json
}

resource "aws_iam_role_policy_attachment" "access" {
  policy_arn = aws_iam_policy.access.arn
  role       = aws_iam_role.streaming.name
}

data "aws_iam_policy_document" "access" {
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["*"]
    effect = "Allow"
  }
  statement {
    actions = [
      "dynamodb:GetShardIterator",
      "dynamodb:DescribeStream",
      "dynamodb:GetRecords"
    ]
    resources = ["*"]
    effect    = "Allow"
  }
  statement {
    actions = [
      "es:ESHttpPost"
    ]
    resources = ["*"]
    effect    = "Allow"
  }  
  statement {
    actions = [
      "iam:CreateServiceLinkedRole"
    ]
    resources = ["arn:aws:iam::*:role/aws-service-role/opensearchservice.amazonaws.com/*"]
    effect    = "Allow"
  }
  statement {
            effect = "Allow"
            actions =  ["aoss:APIAccessAll"]
            resources = ["arn:aws:aoss:us-west-2:176885971431:collection/collection-id"]
  }
  statement {
            effect = "Allow"
            actions = ["aoss:DashboardsAccessAll"]
            resources = ["arn:aws:aoss:us-west-2:176885971431:dashboards/default"]
  }
    
}