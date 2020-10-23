resource "aws_security_group" "master_security_group" {
  name        = "master_security_group"
  description = "Allow inbound traffic from VPN"
  vpc_id      = aws_vpc.main-VPC.id

  # Avoid circular dependencies stopping the destruction of the cluster
  revoke_rules_on_delete = true
 
  # Allow communication between nodes in the VPC
  ingress {
    from_port   = "0"
    to_port     = "0"
    protocol    = "-1"
    self        = true
  }
 
  ingress {
      from_port   = "8443"
      to_port     = "8443"
      protocol    = "TCP"
  }
 
  egress {
    from_port   = "0"
    to_port     = "0"
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
 
  # Allow SSH traffic from VPN
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "TCP"
    cidr_blocks = ["0.0.0.0/0"]
  }
 
  #### Expose web interfaces to VPN
 
  # Yarn
  ingress {
    from_port   = 8088
    to_port     = 8088
    protocol    = "TCP"
    cidr_blocks = [aws_vpc.main-VPC.cidr_block]
  }
 
  # Spark History
  ingress {
      from_port   = 18080
      to_port     = 18080
      protocol    = "TCP"
      cidr_blocks = [aws_vpc.main-VPC.cidr_block]
    }
 
  # Zeppelin
  ingress {
      from_port   = 8890
      to_port     = 8890
      protocol    = "TCP"
      cidr_blocks = [aws_vpc.main-VPC.cidr_block]
  }
 
  # Spark UI
  ingress {
      from_port   = 4040
      to_port     = 4040
      protocol    = "TCP"
      cidr_blocks = [aws_vpc.main-VPC.cidr_block]
  }
 
  # Ganglia
  ingress {
      from_port   = 80
      to_port     = 80
      protocol    = "TCP"
      cidr_blocks = [aws_vpc.main-VPC.cidr_block]
  }
 
  # Hue
  ingress {
      from_port   = 8888
      to_port     = 8888
      protocol    = "TCP"
      cidr_blocks = [aws_vpc.main-VPC.cidr_block]
  }
 
  lifecycle {
    ignore_changes = [ingress, egress]
  }
}

resource "aws_security_group" "slave_security_group" {
  name        = "slave_security_group"
  description = "Allow all internal traffic"
  vpc_id      = aws_vpc.main-VPC.id
  
  revoke_rules_on_delete = true
 
  # Allow communication between nodes in the VPC
  ingress {
    from_port   = "0"
    to_port     = "0"
    protocol    = "-1"
    self        = true
  }
 
  ingress {
      from_port   = "8443"
      to_port     = "8443"
      protocol    = "TCP"
  }
 
  egress {
    from_port   = "0"
    to_port     = "0"
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
 
  # Allow SSH traffic from VPN
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "TCP"
    cidr_blocks = ["0.0.0.0/0"]
  }
 
  lifecycle {
    ignore_changes = [ingress, egress]
  }
}