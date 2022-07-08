import os

import firebase_admin
import structlog
from firebase_admin import credentials, firestore

PROJECT_ID = os.environ["PROJECT_ID"]

logger = structlog.get_logger(__name__)
root = os.path.dirname(os.path.abspath(__file__))

cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(
    cred,
    {
        "projectId": PROJECT_ID,
    },
)
db = firestore.client()

def update_document_to_firestore(object: dict, id: str, collection: str):
    doc_ref = db.collection(collection).document(id)
    doc_ref.update(object)


def find_document_in_firestore(key: str, id: str, collection: str):
    return db.collection(collection).where(key, "==", id).get()

experience_uids = [
    "a071aeaa-9178-4d73-af9a-26b4c9491e32",
    "a93b9823-62d3-4129-8d23-a5accfa10f10",
    "c8c45b99-311d-499d-b4ca-b2ef1de6144d",
    "e4245875-f86f-4e5a-b400-19b1aa1f549e",
    "929a05df-66e9-4c8f-978f-10cdee4457de",
    "5f5b4ae2-5e33-4174-83f4-fb2a58c8c099",
    "1e99cb5c-3790-47e0-97b8-32fcd2171ceb",
    "c61fdb4d-d3d7-4edd-b40a-ca4b907ef38b",
    "337c7512-277c-4f26-933f-f72f9f3e6314",
    "c1f15448-37f2-47b1-86ca-fbe93674b7d7",
    "491c33cc-b773-40e2-8cbf-dbe66a8bc8cf",
    "c516992b-c413-4160-941f-592c8a190c9b",
    "fff6d7db-0872-440c-ac47-44c55f8b5995",
    "84dcdcf6-b7b7-4c45-84d5-4bb157977c3d",
    "91cc96e5-585b-44a4-b507-05e650f7c4e1",
    "f59e0394-b753-42fe-b352-fd1935c5add6",
    "703a8060-3448-45ed-a83b-cf4f004e9398",
    "d8e61a40-f282-43e8-a484-3e8e4b8bc110",
    "2109372b-898a-4767-9953-e78edbb3e561",
    "c5ce067f-d916-4931-aba9-e413f528677c",
    "0ab5f386-8583-431e-8aca-35c6a0e50f34",
    "f51617a7-d417-4253-a7b3-ca44079f12a2",
    "3b8435c9-95f1-4334-90a3-cb773573e783",
    "b8698a62-a575-4cdb-a70d-ea92db64699b",
    "82d32979-a162-4b00-b30d-9c1d2193d815",
    "08a50a9f-ac60-4ade-9b65-6327ecd69522",
    "2e2bebd5-1440-437d-b3d9-3083a7f57cfa",
    "9e2e1ae1-c0c5-4949-90aa-ceb0023c4eea",
    "85439f4c-e74c-4c3d-af5c-f8fdd56ef76f",
    "9018cc75-7eaf-4b20-87dc-ed015ac8e53b",
]

for experience_uid in experience_uids:
    experiences = find_document_in_firestore(
        "uid", experience_uid, "experiences"
    )
    experience_object = experiences[0].to_dict()

    posts = find_document_in_firestore(
        "experience_summary.uid", experience_uid, "posts"
    )
    for post in posts:
        post_object = post.to_dict()
        summary = {
            "experience_summary.location": experience_object["location"]
        }
        update_document_to_firestore(summary, post_object["uid"], "posts")