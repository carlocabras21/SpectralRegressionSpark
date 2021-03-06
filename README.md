# Calcolo redshift fotometrico su diversi cluster EMR di AWS

## Tutorial

Innanzitutto scaricare la cartella per intero. La cartella `results` contiene i risultati dei miei test e non serve ai fini dell'esecuzione del progetto.

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

Ricaricare la pagina che ci si presenta fino a quando la query no passerà a "Finished". Possiamo quindi cliccare su "MyDB" dove troviamo la tabella `spectral_data_class`, clicchiamoci sopra.

Clicchiamo su "Download", selezioniamo "Comma Separated Values" dal menu a tendina indicante il formato del file, e premiamo "Go". Quando il file sarà pronto ci sarà il pulsante "Download", salviamo il file all'interno della cartella `resources`.

### AWS e Terraform
Installare aws-cli https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html

Installare Terraform https://learn.hashicorp.com/tutorials/terraform/install-cli

Creare un account su AWS Edcuate https://aws.amazon.com/it/education/awseducate/

Dopo  aver effettuato il login su AWS Educate, cliccare in alto a destra su "AWS Account", poi nel bottone centrale "AWS Edcuate Starter Account". Ci troviamo davanti la pagina di Vocareum da cui possiamo controllare quanti crediti ci rimangono ed accedere ad AWS.

Accedere ad AWS tramite "AWS Console"

Da "Servizi" in alto a sinistra, andare su "EC2". Nella sezione "Risorse" al centro della pagina, clicchiamo quindi su "Coppie di chiavi", poi su "Crea una coppia di chiavi". Inseriamo il nome, ad esempio "chiave", scegliamo come formato "pem" e clicchiamo su "Crea una coppia di chiavi". Salviamo il file `chiave.pem` all'interno della cartella principale del progetto.

Cambiare i permessi con `chmod 400 chiave.pem` in modo che solo il nostro utente possa leggerla.

### Credenziali
Dalla pagina Vocareum, clicchiamo su "Account Details". Sotto la voce "AWS CLI" clicchiamo il pulsante "Show". Copiamo ed incolliamo le credenziali nel file `access_variables.tf`, in questo modo:

Il valore di `aws_access_key` dentro Vocareum assegnarlo al campo `default` di `access-key` in `access_variables.tf`, come stringa. 

Il valore di `aws_secret_access` dentro Vocareum assegnarlo al campo `default` di `secret-key` in `access_variables.tf`, come stringa.  

Il valore di `aws_session_token` dentro Vocareum assegnarlo al campo `default` di `token`  in `access_variables.tf`, come stringa.  



## Esecuzione con 2 istanze m4

### Impostazione e creazione cluster
In `cluster.tf`:  

`212. instance_type  = "m4.large"`  
`213. instance_count = 2`.  

Da un terminale aperto nella cartella del progetto, creare il cluster lanciando `terraform apply --auto-approve`

Verificare che tutto sia avvenuto correttamente connettendosi via SSH con

`ssh -i chiave.pem hadoop@<public-dns>` dove `<public-dns>` è l'indirizzo che terraform ha restituito come output.

Una volta connessi, tornare in locale premendo `Ctrl + D`.

### Impostazione script
In `SpectralRegressionSpark.py`, impostare:

`20. test                = False`   
`21. write_results_in_S3 = True`    

`24. two_classes_dataset = False`   

`31. regression_type = "linear"`    
`32. # regression_type = "decision-tree"`   
`33. # regression_type = "random-forest"`   

`36. test_on_single_classes = True` 

`40. slaves = "2xm4large"`  

### Lancio script

Inviare lo script via SSH al cluster tramite il comando `scp` in un terminale sempre nella cartella del progetto:

`scp -i chiave.pem SpectralRegressionSpark.py hadoop@<public-dns>:∼/`   

Connettersi nuovamente tramite SSH:

`ssh -i chiave.pem hadoop@<public-dns>` 

Lanciare lo script con:

`spark-submit --deploy-mode cluster SpectralRegressionSpark.py` 

Attendere che lo script finisca.

I risultati relativi a rmse e tempi di calcolo si troveranno nella cartella `S3/spectral-regression-spark-bucket/results_2xm4large_linear_<date-time>` all'interno del file `PART-00000`.   

**Lanciare lo script nuovamente impostando  `regression_type = "decision-tree"`**

**Lanciare lo script nuovamente impostando  `regression_type = "random-forest"`**

## Esecuzione con altre istanze

Ripetere i tre test precedenti (`regression_type = "linear"`, `regression_type = "decision-tree"`, `regression_type = "random-forest"`) creando cluster con 4 e 8 istanze `m4.large`, poi nuovamente con 2, 4 e 8 istanze `c4.large`.

Ogni volta che si cambia tipo di cluster, impostare dentro `SpectralRegressionSpark.py` alla riga 40 `slaves = ...` il tipo di configurazione, ad esempio se si usano 4 istanze `c4.large`, scrivere `slaves = "4xc4large"`.


## Esecuzione su due sole classi del dataset

Creare un cluster con 4 istanze `c4.large`.

Dentro `SpectralRegressionSpark.py` impostare:

`20. test                = False`   
`21. write_results_in_S3 = True`    

`24. two_classes_dataset = True`    
`26. filter_type = "star-galaxy"`   
`27. # filter_type = "star-qso"`    
`28. # filter_type = "galaxy-qso"`  

`31. regression_type = "linear"`    
`32. # regression_type = "decision-tree"`   
`33. # regression_type = "random-forest"`   

`36. test_on_single_classes = True` 

`40. slaves = "4xc4large"`


**Per ogni `filter_type`, lanciare gli script eseguendo tutti e tre i `regression_type`**

## Risultati

I risultati si troveranno all'interno della cartella `results`, suddivisi per categorie di test.
