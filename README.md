# Pinterest Data Pipeline using AWS, Databricks, Spark, Airflow, Kinesis, Kafka and API Gateway

Pinterest crunches billions of data points every day to decide how to provide more value to their users. 

In this project, we will create a similar system using the AWS Cloud.

## Setting up the Pinterest infrastructure

To begin, I will need infrastructure similar to what a Pinterest data engineer would be working with. For this I used the user_posting_emulation.py script. This script contains login details for a RDS database with three tables that resemble the data received by the Pinterest API when a POST request is made by a user uploading data. This will provide us with the data to work with throughout the project. 

The three tables in the RDS include: 

    1. pinterest_data: contains data about posts being uploaded to Pinterest.
    2. geolocation_data: contains data about the geolocation of each Pinterest post found in pinterest_data
    3. user_data: contains data about the user that has uploaded each post found in pinterest_data

## Configuring the EC2 Kafka Client

In this step we will be configuring an EC2 instance to use as a Kafka Client to perform batch processing of the Pinterest data. The EC2 instance has already been created and deployed, for information on how to achieve this please look [here](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html).

1. Save the .pem file specific to your EC2 instance locally. This will allow us to connect to our client machine via SSH. 

Remember to either include this file in your .gitignore or use Github Secrets to ensure this doesn't get compromised. 

2. Connect to the EC2 instance via SSH:
```bash
ssh -i /path/key-pair-name.pem instance-user-name@instance-public-dns-name
```
3. An IAM authenticated MSK cluster has already been setup, to connect to this cluster we will have to install the appropriate packages:

- First we will need to install Java on our instance by running the following command:
```bash
sudo yum install java-1.8.0
```

- Next we will install and unzip Apache Kafka on our EC2 instance making sure it is the same version as the one our MSK cluster is running on. 

```bash
wget https://archive.apache.org/dist/kafka/2.8.1/kafka_2.12-2.8.1.tgz
tar -xzf kafka_2.12-2.8.1.tgz
```

- Our MSK Cluster uses IAM authentication to ensure safe security practices regarding an organisations resources. To connect to the cluster we will need to install additional steps by firstly navigating to the 'libs' folder of our kafka installation folder:

```bash
cd kafka_2.12-2.8.1/libs/
```
Then downloading the IAM MSK authentication package from Github, using the following command. This package is necessary to connect to MSK Clusters that require IAM authentication:

```bash
wget https://github.com/aws/aws-msk-iam-auth/releases/download/v1.1.5/aws-msk-iam-auth-1.1.5-all.jar
```
- Before our EC2 instance is able to use IAM for cluster authentication we will need to edit the trust policy in our IAM console. For this:

```
Navigate to the IAM console on your AWS account

Here, on the left hand side select the Roles section

You should see a list of roles, select the one corresponding to your EC2 instance

Copy this role ARN and make a note of it, as we will be using it later for the cluster authentication

Go to the Trust relationships tab and select Edit trust policy

Click on the Add a principal button and select IAM roles as the Principal type

Replace ARN with the ARN you have just copied 
```

- To ensure the Amazon MSK IAM libraries are accessible to the Kafka client we will need to set up a CLASSPATH variable. This will allow the client to locate and utilise the necessary libraries. 

    To do this we can use the following command
```bash
export CLASSPATH=/path/aws-msk-iam-auth-1.1.5-all.jar
```

additionally, we can add this command to our ./bashrc file to ensure this environment variable persists across sessions. 

- Next we need to add the configuration settings in a 'client.properties' file in the bin folder of our kafka installation. 

    To do this first navigate to the bin folder of your kafka installation
```bash
cd kafka_2.12-2.8.1/bin/
```
Create a client.properties file:
```bash
nano client.properties
```
Edit this file to include the following configuration settings:
```bash
# Sets up TLS for encryption and SASL for authN.
security.protocol = SASL_SSL

# Identifies the SASL mechanism to use.
sasl.mechanism = AWS_MSK_IAM

# Binds SASL client implementation.
sasl.jaas.config = software.amazon.msk.auth.iam.IAMLoginModule required awsRoleArn="Your Access Role";

# Encapsulates constructing a SigV4 signature based on extracted credentials.
# The SASL client bound by "sasl.jaas.config" invokes this class.
sasl.client.callback.handler.class = software.amazon.msk.auth.iam.IAMClientCallbackHandler
```
4. The final part concerning configuration of the instance is to create the topics for the cluster we will be using. We will need to create three topics, each corresponding to one of the RDS tables referenced in our user_posting_emulation.py script. 

- First we will need to head to the MSK Console on AWS to retrieve the Bootstrap servers string and the Plaintext Apache Zookeeper connection string for our cluster. These will allow us to connect to the cluster and create topics. Save these strings. 

- To create a topic we need to first make sure we are in the /bin folder of our kafka installation. From here we can run the following command to create a topic. Replacing the BootstrapServerString and <topic_name> with the values required. 

```bash
./kafka-topics.sh --bootstrap-server BootstrapServerString --command-config client.properties --create --topic <topic_name>
```

    






