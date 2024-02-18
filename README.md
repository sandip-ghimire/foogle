### Application overview
A personal search assistant with custom data feed option. It can be personalized to add your own files (pdf/txt) or links/url to extract the information from them and feed llm model.
Based on GPT-3.5 Turbo model and langchain framework.

### Running the application
##### Requirements
- For running the application in docker container, **Docker** needs to be installed in the system if not already installed. Please follow the instruction for the installation: https://docs.docker.com/get-docker/

- Register and get API key from OpenAI (https://platform.openai.com/api-keys).

- Clone the project repo: git clone https://github.com/sandip-ghimire/foogle

##### Steps
- Open the command line from the root directory of the project, i.e. the path where Dockerfile is located.  Build the docker image with the command:
  >docker build -t foogle .

- Add the environment variables in .env file. OPENAI_API_KEY provided by OpenAI and a random SECRET_KEY for django application. 

- Run the docker container with the command below: <br />
  >docker run --name=foogle-container --env-file .env -d -p 8008:8008 foogle

  *(The application runs on port 8008)* <br />
  The interface can be accessed at: <br />
  http://localhost:8008/
