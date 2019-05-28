# Setup
To run the client and API, follow these steps:

1. Untar the Odyssey statistics tarball into the `./data` folder
2. Run the system using docker-compose, i.e. `docker-compose up -d`

# Important directories
- The API source is located at `./api/pipe`
- The client source is located at `./client/src`

# Todos
- Include engine dependency compilation as part of the API Dockerfile
- Add a lock to ensure only one query is executed at once
