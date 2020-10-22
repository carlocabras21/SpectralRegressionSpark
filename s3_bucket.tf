
# bucket che conterrà script e dati
resource "aws_s3_bucket" "main-bucket" {
  bucket = "spectral-regression-spark-bucket" # assegnare un nome univoco GLOBALE alla risorsa
}

# upload dei dati di test
resource "aws_s3_bucket_object" "test-data-upload" {
  bucket = aws_s3_bucket.main-bucket.id
  key    = "test.csv" # nome che il file avrà dentro il bucket
  source = "resources/test.csv"
}

# # upload dei dati veri e propri
# resource "aws_s3_bucket_object" "test-data-upload" {
#   bucket = aws_s3_bucket.main-bucket.id
#   key    = "spectral_data_class.csv" # nome che il file avrà dentro il bucket
#   source = "resources/spectral_data_class.csv"
# }

# upload dello script
resource "aws_s3_bucket_object" "script-upload" {
  bucket = aws_s3_bucket.main-bucket.id
  key    = "SpectralRegressionSpark.py" # nome che il file avrà dentro il bucket
  source = "SpectralRegressionSpark.py"
}

# upload del file di output
resource "aws_s3_bucket_object" "output-upload" {
  bucket = aws_s3_bucket.main-bucket.id
  key    = "output.txt" # nome che il file avrà dentro il bucket
  source = "output.txt"
}

# endpoint per la VPC
resource "aws_vpc_endpoint" "s3" {
  vpc_id = aws_vpc.main-VPC.id
  service_name = "com.amazonaws.us-east-1.s3"
}

resource "aws_vpc_endpoint_route_table_association" "route_table_association" {
  route_table_id = aws_route_table.main-route-table.id
  vpc_endpoint_id = aws_vpc_endpoint.s3.id
}

# bucket che conterrà i file di log
resource "aws_s3_bucket" "log-bucket" {
  bucket = "log-spectral-regression-spark-bucket" # assegnare un nome univoco GLOBALE alla risorsa
}
