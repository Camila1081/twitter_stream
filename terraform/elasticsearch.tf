resource "aws_opensearch_domain" "main" {
  domain_name           = "elasticsearch"
  engine_version = "Elasticsearch_7.10"

  cluster_config {
    zone_awareness_enabled = false
    instance_type          = "c5.large.search"
    instance_count         = 1
  }

  ebs_options {
    ebs_enabled = true
    volume_type = "gp2"
    volume_size = 10
  }


  access_policies = data.aws_iam_policy_document.main.json
  node_to_node_encryption {
    enabled = true
  }
  encrypt_at_rest {
    enabled = true
  }
  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }
  advanced_security_options {
    enabled                        = true
    internal_user_database_enabled = true
    master_user_options {
      master_user_name     = "camila1081"
      master_user_password = "TopSecret0*"
    }
  }
  
}

data "aws_iam_policy_document" "main" {
  statement {
    principals {
      type        = "AWS"
      identifiers  = ["*"]
    }
    effect  = "Allow"
    actions = ["es:*"]
    resources = ["arn:aws:es:us-west-2:176885971431:domain/elasticsearch/*"]
  }
}