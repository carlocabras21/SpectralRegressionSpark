# Photometric Redshift Regression using EMR clusters created via Terraform

## Tutorial

Scaricare la cartella per intero.

### Dataset
Andare su http://skyserver.sdss.org/CasJobs/SubmitJob.aspx ed effettuare il login, eventualmente creando un account nel caso non se ne fosse
in possesso. Ci troviamo così davanti la schermata da cui possiamo scrivere una query.

Dal menu a tendina "Context", scegliere "DR16".

Scrivere la seguente query:
```
SELECT spectroFlux_u , spectroFlux_g , spectroFlux_r , spectroFlux_i ,
spectroFlux_z , class AS source_class , z AS redshift
INTO MyDB.spectral_data_class
FROM SpecObj
```

e lanciarla cliccando sul pulsante "Submit" presente sulla destra.
Quando la query passerà a "Finished" possiamo cliccare su "MyDB" dove troviamo la tabella spectral_data_class, clicchiamoci sopra.

Clicchiamo su "Download", selezioniamo "Comma Separated Values" dal menu a tendina indicante il formato del file, e premiamo "Go". Quando il file sarà pronto ci sarà il pulsante "Download", salviamo il file all'interno della cartella /resources.

### AWS e Terraform
Installare aws-cli https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html

Installare Terraform https://learn.hashicorp.com/tutorials/terraform/install-cli

Creare un account su AWS Edcuate https://aws.amazon.com/it/education/awseducate/
Dopo  aver effettuato il login, cliccare in alto a destra su "AWS Account", poi nel bottone centrale "AWS Edcuate Starter Account". Ci troviamo davanti la pagina di Vocareum da cui possiamo controllare quanti crediti ci rimangono ed accedere ad AWS.

Accedere ad AWS tramite "AWS Console"

Da "Servizi" in alto a sinistra, andare su "EC2". Nella sezione "Risorse" al centro della pagina, clicchiamo quindi su "Coppie di chiavi", poi su "Crea una coppia di chiavi". Inseriamo il nome, ad esempio "chiave", scegliamo come formato "pem" e clicchiamo su "Crea una coppia di chiavi". Salviamo il file chiave.pem all'interno della cartella principale del progetto.

### Credenziali
Dalla pagina Vocareum, clicchiamo su "Account Details". Sotto la voce "AWS CLI" clicchiamo il pulsante "Show". Copiamo le credenziali nel file access_variables.tf



## Esecuzione con istanze m4

### Impostazione cluster
In cluster.tf, riga 212, impostare instance_type = "m4.large". Riga 213, instance_count = 2.

### Impostazione script
In SpectralRegressionSpark.py, impostare:
20. test                = False  # to use data from test.csv, a small portion of the dataset
21. write_results_in_S3 = True

24. two_classes_dataset = False

31. regression_type = "linear"
32. <commentare>
33. <commentare>    

40. slaves = "2xm4large"

