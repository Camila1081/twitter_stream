resource "aws_s3_bucket" "tos3" {
  bucket = "ddbs3-twitter-itau"

  tags = {
    Name        = "My bucket"
    Environment = "Dev"
  }
}