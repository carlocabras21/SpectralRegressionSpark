/*
# creazione bucket
resource "aws_s3_bucket" "main-bucket" {
  bucket = "spectral-regression-spark-bucket" # assegnare un nome univoco GLOBALE alla risorsa
}

# upload di file dentro il bucket
resource "aws_s3_bucket_object" "file-upload" {
  bucket = aws_s3_bucket.main-bucket.id
  key    = "test.csv" # nome che il file avrà dentro il bucket
  source = "src/main/resources/test.csv"
}
*/