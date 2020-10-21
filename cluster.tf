# Build Infrastructure
# https://learn.hashicorp.com/tutorials/terraform/aws-build

# Setting Up an AWS EC2 instance with SSH access using Terraform
# https://medium.com/@hmalgewatta/setting-up-an-aws-ec2-instance-with-ssh-access-using-terraform-c336c812322f

# Can i do ssh into my ec2 instance created by terraform?
# https://stackoverflow.com/questions/59708577/can-i-do-ssh-into-my-ec2-instance-created-by-terraform


# Resource: aws_emr_cluster, Example bootable config
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/emr_cluster#example-bootable-config



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


###

# IAM Role setups

###

# IAM role for EMR Service
resource "aws_iam_role" "iam_emr_service_role" {
  name = "iam_emr_service_role"

  assume_role_policy = <<EOF
{
  "Version": "2008-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "elasticmapreduce.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "iam_emr_service_policy" {
  name = "iam_emr_service_policy"
  role = aws_iam_role.iam_emr_service_role.id

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Resource": "*",
        "Action": [
            "ec2:AuthorizeSecurityGroupEgress",
            "ec2:AuthorizeSecurityGroupIngress",
            "ec2:CancelSpotInstanceRequests",
            "ec2:CreateNetworkInterface",
            "ec2:CreateSecurityGroup",
            "ec2:CreateTags",
            "ec2:DeleteNetworkInterface",
            "ec2:DeleteSecurityGroup",
            "ec2:DeleteTags",
            "ec2:DescribeAvailabilityZones",
            "ec2:DescribeAccountAttributes",
            "ec2:DescribeDhcpOptions",
            "ec2:DescribeInstanceStatus",
            "ec2:DescribeInstances",
            "ec2:DescribeKeyPairs",
            "ec2:DescribeNetworkAcls",
            "ec2:DescribeNetworkInterfaces",
            "ec2:DescribePrefixLists",
            "ec2:DescribeRouteTables",
            "ec2:DescribeSecurityGroups",
            "ec2:DescribeSpotInstanceRequests",
            "ec2:DescribeSpotPriceHistory",
            "ec2:DescribeSubnets",
            "ec2:DescribeVpcAttribute",
            "ec2:DescribeVpcEndpoints",
            "ec2:DescribeVpcEndpointServices",
            "ec2:DescribeVpcs",
            "ec2:DetachNetworkInterface",
            "ec2:ModifyImageAttribute",
            "ec2:ModifyInstanceAttribute",
            "ec2:RequestSpotInstances",
            "ec2:RevokeSecurityGroupEgress",
            "ec2:RunInstances",
            "ec2:TerminateInstances",
            "ec2:DeleteVolume",
            "ec2:DescribeVolumeStatus",
            "ec2:DescribeVolumes",
            "ec2:DetachVolume",
            "iam:GetRole",
            "iam:GetRolePolicy",
            "iam:ListInstanceProfiles",
            "iam:ListRolePolicies",
            "iam:PassRole",
            "s3:CreateBucket",
            "s3:Get*",
            "s3:List*",
            "sdb:BatchPutAttributes",
            "sdb:Select",
            "sqs:CreateQueue",
            "sqs:Delete*",
            "sqs:GetQueue*",
            "sqs:PurgeQueue",
            "sqs:ReceiveMessage"
        ]
    }]
}
EOF
}

# IAM Role for EC2 Instance Profile
resource "aws_iam_role" "iam_emr_profile_role" {
  name = "iam_emr_profile_role"

  assume_role_policy = <<EOF
{
  "Version": "2008-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_instance_profile" "emr_profile" {
  name = "emr_profile"
  role = aws_iam_role.iam_emr_profile_role.name
}

resource "aws_iam_role_policy" "iam_emr_profile_policy" {
  name = "iam_emr_profile_policy"
  role = aws_iam_role.iam_emr_profile_role.id

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Resource": "*",
        "Action": [
            "cloudwatch:*",
            "dynamodb:*",
            "ec2:Describe*",
            "elasticmapreduce:Describe*",
            "elasticmapreduce:ListBootstrapActions",
            "elasticmapreduce:ListClusters",
            "elasticmapreduce:ListInstanceGroups",
            "elasticmapreduce:ListInstances",
            "elasticmapreduce:ListSteps",
            "elasticmapreduce:AddJobFlowSteps",
            "kinesis:CreateStream",
            "kinesis:DeleteStream",
            "kinesis:DescribeStream",
            "kinesis:GetRecords",
            "kinesis:GetShardIterator",
            "kinesis:MergeShards",
            "kinesis:PutRecord",
            "kinesis:SplitShard",
            "rds:Describe*",
            "s3:*",
            "sdb:*",
            "sns:*",
            "sqs:*"
        ]
    }]
}
EOF
}

resource "aws_emr_cluster" "cluster" {
  name = "emr-test-arn"
  release_label = "emr-4.6.0"
  applications = [
    "Spark"]

  service_role = aws_iam_role.iam_emr_service_role.arn

  termination_protection = false
  keep_job_flow_alive_when_no_steps = true

  ec2_attributes {
    key_name      = var.key_name
    subnet_id = aws_subnet.subnet-uno.id
    # emr_managed_master_security_group = aws_security_group.ingress-all.id
    # emr_managed_slave_security_group = aws_security_group.ingress-all.id
    emr_managed_master_security_group = aws_security_group.master_security_group.id
    emr_managed_slave_security_group = aws_security_group.slave_security_group.id
    instance_profile = aws_iam_instance_profile.emr_profile.arn

  }

  master_instance_group {
    instance_type = "m4.large"
  }

  core_instance_group {
    instance_type = "c4.large"
    instance_count = 2

    ebs_config {
      size                 = "40"
      type                 = "gp2"
      volumes_per_instance = 1
    }

  }

}

// non funziona e non ho neanche capito a cosa serva
//resource "aws_emr_instance_group" "task" {
//  cluster_id     = aws_emr_cluster.cluster.id
//  instance_count = 1
//  instance_type  = "c4.large"
//  name           = "my little instance group"
//}



# print the public dns in order to connect it via ssh
# ssh -i "<key_name>.pem" <username>@<public_dns>
# where <username> = hadoop
output "public_dns" {
  description = "The public ip for ssh access"
  value       = aws_emr_cluster.cluster.master_public_dns
}

output "id" {
  description = "cluster id"
  value       = aws_emr_cluster.cluster.id
}





