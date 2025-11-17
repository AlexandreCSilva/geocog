import ee
from dotenv import load_dotenv
import os

class GEEManager:
    def __init__(self):
        load_dotenv()
        self.project_name = os.getenv("PROJECT_NAME")

    def initialize(self):
        ee.Authenticate()
        ee.Initialize(project=self.project_name)
