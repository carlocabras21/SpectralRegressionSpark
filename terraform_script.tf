# Build Infrastructure
# https://learn.hashicorp.com/tutorials/terraform/aws-build

# Setting Up an AWS EC2 instance with SSH access using Terraform
# https://medium.com/@hmalgewatta/setting-up-an-aws-ec2-instance-with-ssh-access-using-terraform-c336c812322f

# Can i do ssh into my ec2 instance created by terraform?
# https://stackoverflow.com/questions/59708577/can-i-do-ssh-into-my-ec2-instance-created-by-terraform


terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 2.70"
    }
  }
}


provider "aws" {
  region     = "us-east-1"
  
  # questi dati vanno presi ogni volta da "Account Details" dentro vocareum
  access_key = var.access-key # values inside an external .tf file
  secret_key = var.secret-key
  token = var.token
}

resource "aws_instance" "main_instance" {
  # prendere questi codici dalla console aws
  ami           = "ami-0dba2cb6798deb6d8"
  instance_type = "t2.micro"

  key_name      = var.key_name # a key-pair that I have created

  # originally security_groups but it wasn't working
  vpc_security_group_ids = [aws_security_group.ingress-all.id]

  subnet_id = aws_subnet.subnet-uno.id
}

# print the public dns in order to connect it via ssh
# ssh -i "<key_name>.pem" <username>@<public_dns>
# where <username> = ubuntu
output "public_dns" {
  description = "The public ip for ssh access"
  value       = aws_instance.main_instance.public_dns
}


# setup the VPC
resource "aws_vpc" "main-VPC" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support = true
}

# set up a subnet in our newly created VPC
resource "aws_subnet" "subnet-uno" {
  cidr_block = cidrsubnet(aws_vpc.main-VPC.cidr_block, 3, 1)
  vpc_id = aws_vpc.main-VPC.id
  availability_zone = "us-east-1a"
}

# define a security group that will allow anyone to connect through port 22.
# it will also forward all traffic without restriction
resource "aws_security_group" "ingress-all" {
  name = "allow-all-sg"
  vpc_id = aws_vpc.main-VPC.id
  ingress {
    cidr_blocks = [
      "0.0.0.0/0"
    ]
    from_port = 22
    to_port = 22
    protocol = "tcp"
  }
  // Terraform removes the default rule
  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


# attaching an elastic IP to be able to access the instance
resource "aws_eip" "elastic-IP" {
  instance = aws_instance.main_instance.id
  vpc      = true
}

# Setting up an internet gateway in order to route traffic from the internet to our VPC
resource "aws_internet_gateway" "main-gateway" {
  vpc_id = aws_vpc.main-VPC.id
}

# Setting up route tables
resource "aws_route_table" "main-route-table" {
  vpc_id = aws_vpc.main-VPC.id
  route {
      cidr_block = "0.0.0.0/0"
      gateway_id = aws_internet_gateway.main-gateway.id
    }
}

resource "aws_route_table_association" "subnet-association" {
  subnet_id      = aws_subnet.subnet-uno.id
  route_table_id = aws_route_table.main-route-table.id
}



# assegnare un nome univoco GLOBALE alla risorsa
resource "aws_s3_bucket" "main-bucket" {
  bucket = "spectral-regression-spark-bucket"
}

resource "aws_s3_bucket_object" "file-upload" {
  bucket = aws_s3_bucket.main-bucket.id
  key    = "test.csv" # nome che il file avrà dentro il bucket
  source = "src/main/resources/test.csv"
}


