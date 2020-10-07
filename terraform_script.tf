terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 2.70"
    }
  }
}

# Can i do ssh into my ec2 instance created by terraform?
# https://stackoverflow.com/questions/59708577/can-i-do-ssh-into-my-ec2-instance-created-by-terraform

# How do I create an SSH key in Terraform?
# https://stackoverflow.com/questions/49743220/how-do-i-create-an-ssh-key-in-terraform

provider "aws" {
  region     = "us-east-1"
  
  # questi dati vanno presi ogni volta da "Account Details" dentro vocareum
  # NASCONDERLI QUANDO CARICARE SU GITHUB
  access_key = ""
  secret_key = ""
  token = ""
}

# prendere questi codici dalla console aws
resource "aws_instance" "main_instance" {
  ami           = "ami-0dba2cb6798deb6d8"
  instance_type = "t2.micro"
}

# assegnare un nome univoco GLOBALE alla risorsa
resource "aws_s3_bucket" "main_bucket" {
  bucket = "spectral-regression-spark-bucket"
}

resource "aws_s3_bucket_object" "file_upload" {
  bucket = aws_s3_bucket.main_bucket.id
  key    = "test.csv" # nome che il file avrà dentro il bucket
  source = "src/main/resources/test.csv"
}