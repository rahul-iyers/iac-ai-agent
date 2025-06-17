provider "aws" {
  region = "us-east-3"
}

resource "aws_s3_bucket" "unsecure_bucket" {
  bucket = "my-public-bucket-123456"
  acl    = "public-read"
}

resource "aws_security_group" "open_sg" {
  name        = "open_sg"
  description = "Allow all traffic"

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
