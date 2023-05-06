resource "aws_elasticsearch_domain" "main" {
  domain_name           = "elasticsearch"
  elasticsearch_version = "7.10"

  cluster_config {
    zone_awareness_enabled = false
    instance_type          = "c5.large.elasticsearch"
    instance_count         = 1
  }

  ebs_options {
    ebs_enabled = true
    volume_type = "gp2"
    volume_size = 10
  }
  vpc_options {
    subnet_ids         = [aws_subnet.subnet_for_lambda.id]
    security_group_ids = [aws_security_group.sg_for_lambda.id]
  }


  advanced_options = {
    "rest.action.multi.allow_explicit_index" = "true"
  }

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  encrypt_at_rest {
    enabled = true
  }

  node_to_node_encryption {
    enabled = true
  }

  access_policies = data.aws_iam_policy_document.main.json
}
data "aws_iam_policy_document" "main" {
  statement {
    principals {
      type        = "AWS"
      identifiers  = ["*"]
    }
    effect  = "Allow"
    actions = ["es:*"]
  }
}