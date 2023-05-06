resource "aws_iam_role" "streaming" {
  name               = "streaming"
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
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "subnet_for_lambda" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
  availability_zone = "us-west-2b"

  tags = {
    Name = "vpc_lambda_es"
  }
}
resource "aws_security_group" "sg_for_lambda" {
  name_prefix = "sg_for_lambda"
  vpc_id = aws_vpc.main.id
 
  ingress {
    from_port = 0
    to_port = 65535
    protocol = "tcp"
    cidr_blocks = ["10.0.1.0/24"]
  }
 
  egress {
    from_port = 0
    to_port = 65535
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}




resource "aws_iam_role_policy_attachment" "vpc_access" {
  policy_arn = data.aws_iam_policy.vpc_access.arn
  role       = aws_iam_role.streaming.name
}
data "aws_iam_policy" "vpc_access" {
  arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_policy" "access" {
  name   = "streaming"
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
    resources = values(data.aws_dynamodb_table.table)[*].stream_arn
    effect    = "Allow"
  }
  statement {
    actions = [
      "es:ESHttpPost"
    ]
    resources = ["*"]
    effect    = "Allow"
  }
}