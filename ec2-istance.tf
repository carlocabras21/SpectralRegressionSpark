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

  key_name      = var.key_name

  # originally security_groups but it wasn't working
  vpc_security_group_ids = [aws_security_group.ingress-all.id]

  subnet_id = aws_subnet.subnet-uno.id
}

# attaching an elastic IP to be able to access the instance
resource "aws_eip" "elastic-IP" {
  instance = aws_instance.main_instance.id
  vpc      = true
}

# NON FUNZIONA PIU'
# print the public dns in order to connect it via ssh
# ssh -i "<key_name>.pem" <username>@<public_dns>
# where <username> = ubuntu
output "public_dns" {
  description = "The public ip for ssh access"
  value       = aws_instance.main_instance.public_dns
}


/*
sudo apt-get update
sudo apt-get -y install openjdk-8-jdk
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk

sudo wget http://www.scala-lang.org/files/archive/scala-2.11.8.deb
sudo dpkg -i scala-2.11.8.deb
sudo apt-get update
sudo apt-get install scala

echo "deb https://dl.bintray.com/sbt/debian /" | sudo tee -a /etc/apt/sources.list.d/sbt.list
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2EE0EA64E40A89B84B2DF73499E82A75642AC823
sudo apt-get update
sudo apt-get install sbt


mkdir -p SparkRegressionScala/src/main/{scala,resources}
scp -i prima.pem build.sbt ubuntu@ec2-54-146-189-89.compute-1.amazonaws.com:/home/ubuntu/SparkRegressionScala
scp -i prima.pem src/main/scala/SpectralRegressionSpark.scala ubuntu@ec2-54-146-189-89.compute-1.amazonaws.com:/home/ubuntu/SparkRegressionScala/src/main/scala
scp -i prima.pem src/main/resources/test.csv ubuntu@ec2-54-146-189-89.compute-1.amazonaws.com:/home/ubuntu/SparkRegressionScala/src/main/resources

// UN PO' DA RIVEDERE EH. COMUNQUE https://sparkour.urizone.net/recipes/installing-ec2/
wget http://mirror.cc.columbia.edu/pub/software/apache/spark/spark-3.0.1/spark-3.0.1-bin-hadoop2.7.tgz
sudo tar zxvf spark-3.0.1-bin-hadoop2.7.tgz -C /opt
sudo mv spark-3.0.1-bin-hadoop2.7/ /opt
sudo ln -fs spark-3.0.1-bin-hadoop2.7 ./spark
sudo chown -R ubuntu:ubuntu /opt/spark-3.0.1-bin-hadoop2.7
export SPARK_HOME=/opt/spark
PATH=$PATH:$SPARK_HOME/bin
export PATH
*/