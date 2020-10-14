
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
