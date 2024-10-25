from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import ECS
from diagrams.aws.database import Aurora
from diagrams.aws.network import CloudFront
from diagrams.aws.storage import S3
from diagrams.aws.ml import Lex, Polly
from diagrams.onprem.client import User
from diagrams.onprem.compute import Server
from diagrams.onprem.network import Internet

# Ensure the images folder exists
import os
os.makedirs("images", exist_ok=True)

with Diagram("Architecture Diagram", show=False, direction="LR", filename="images/architecture_diagram"):
    # Frontend Components
    with Cluster("Frontend"):
        user = User("User")
        cloudfront = CloudFront("CloudFront")
        s3_frontend = S3("S3 (Minified JS/HTML)")

    # Backend Components
    with Cluster("Backend"):
        ecs = ECS("ECS Backend")
        lex = Lex("Lex")
        polly = Polly("Polly")
        s3_recording = S3("S3 (Recording)")
        automarker = Server("Automarker")

    # Database Components
    with Cluster("Database"):
        aurora = Aurora("Aurora PostgreSQL Serverless V2")

    # Microservices
    with Cluster("Microservices"):
        microservice = Server("Microservice")

    # Connections
    user >> cloudfront >> s3_frontend
    cloudfront >> ecs
    ecs >> lex
    ecs >> polly >> s3_recording
    s3_recording >> automarker
    automarker >> ecs
    ecs >> aurora
    microservice >> aurora
    microservice >> s3_frontend