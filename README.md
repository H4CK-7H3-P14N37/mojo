# TODOs
- REPORTING_TEAM needs to be updated in the generate_doc function to take an input. This means updating the Report model.
- Page to import scan data, but functionality already exists in superdupperadmin
- Guided flow to import findings and then generate reports 

# Setup
## create persistent SECRET_KEY
### NOTE: this will only give a string to copy/paste into .env file
```
./gen_secret_key.py
```

## Your .env file should look like this with a random string.
```
SECRET_KEY=+7^q$nv1x0asdfasdfasdfasdfasdfasdfasdfasdfasdf$s!*^h
```

## build the image
```
./build.sh
```

## run the image
```
./run.sh
```

## from here, you should be able to open the app locally
```
http://127.0.0.1:8000/
```

## if you go to superdupperadmin, you should be able to use the default creds
```
username: root
password: redteamroxs
```

# Cleanup
## if you want to delete all containers, run this. it will delete the database, containers, finding images, everything.
```
./cleanup.sh
```

## if you want to clean the images, do this
```
docker rmi mojo
```


# Preview of app
![Mojo](pics/mojo.png)
