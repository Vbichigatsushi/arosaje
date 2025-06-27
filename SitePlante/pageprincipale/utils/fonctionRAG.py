import os
import pandas as pd
from SitePlante.CodeSite.settings import BASE_DIR
import random
import torch
import numpy as np
from sentence_transformers import util,SentenceTransformer
from timeit import default_timer as timer
csv_path = os.path.join(BASE_DIR, "pageprincipale/static/data/embeddings.csv")
text_chunks_and_embedding_df_load = pd.read_csv(csv_path)
device = "cuda" if torch.cuda.is_available() else "cpu"
text_chunks_and_embedding_df_load["embedding"]=text_chunks_and_embedding_df_load["embedding"].apply(lambda x: np.fromstring(x.strip("[]"),sep=" "))
embeddings=torch.tensor(np.stack(text_chunks_and_embedding_df_load["embedding"].to_list(),axis=0),dtype=torch.float32 ).to(device) #to device utile après pour torch
pages_and_chuncks = text_chunks_and_embedding_df_load.to_dict(orient="records")

embedding_model = SentenceTransformer(model_name_or_path="all-mpnet-base-v2",device=device)
def retrieve_relevant_resources(query: str, embeddings: torch.tensor,model:SentenceTransformer=embedding_model,n_resources_to_return: int=5,
                                print_time: bool=True):
    """
    Cette fonction retourne le top k scores et indices des embedding par rapport a la demande
    """
    query_embedding=model.encode(query,convert_to_tensor=True)

    # Recupere le dot score
    start_time=timer()
    dot_scores=util.dot_score(query_embedding,embeddings)[0]
    end_time=timer()

    if print_time:
        print(f"[INFO] Temps pris pour les embeddings pour {len(embeddings)} embeddings : {end_time-start_time:.5f}second")
    scores,indices = torch.topk(input=dot_scores,k=n_resources_to_return)
    return scores,indices
def print_top_results_and_scores(query:str,
                                 embeddings:torch.tensor,
                                 pages_and_chunks:list[dict]=pages_and_chuncks,
                                 n_ressources_to_return: int=5):
    score,indices = retrieve_relevant_resources(query=query,embeddings=embeddings,n_resources_to_return=n_ressources_to_return)

    for score,idx in zip(score,indices):
        print(f"score:{score:.4f}")
        print(f"Text:{pages_and_chuncks[idx]['sentence_chunck']}")
        print(f"Page :{pages_and_chuncks[idx]['page_number']}")
        print("\n")
def text_top_results_and_scores(query:str,
                                 embeddings:torch.tensor,
                                 pages_and_chunks:list[dict]=pages_and_chuncks,
                                 n_ressources_to_return: int=5):
    score,indices = retrieve_relevant_resources(query=query,embeddings=embeddings,n_resources_to_return=n_ressources_to_return)
    text_final="Voici les 5 phrases les plus proches dans mon document avec la base vectorielle : "
    for score,idx in zip(score,indices):
        text_final=text_final +"     " +pages_and_chuncks[idx]['sentence_chunck']
    return text_final
from mistralai import Mistral


def rag_with_mistral(query: str, embeddings: dict) -> str:
    """
    Fonction qui interroge le modèle Mistral avec un système de RAG basé sur des embeddings.

    :param query: La question posée par l'utilisateur
    :param embeddings: Un dictionnaire {phrase: vecteur d'embedding}
    :return: La réponse du modèle Mistral
    """

    # Clé API et configuration
    os.environ["MISTRAL_API_KEY"] = "VwEcL08P6LMpj6wk1GqKxyIkW7IIFOZs"
    api_key = os.environ["MISTRAL_API_KEY"]
    model = "mistral-large-latest"

    # Initialisation du client
    client = Mistral(api_key=api_key)

    # Générer le texte via fonction de RAG
    text_embedding = text_top_results_and_scores(query=query, embeddings=embeddings)

    # Formatage de la requête avec les infos RAG
    query_final = f"{text_embedding}    '''{query}'''"

    # Appel à l'API Mistral
    chat_response = client.chat.complete(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu es un jardinier professionnel qui donne des conseils très précis. "
                    "Si la question n'a aucun rapport avec les plantes, dire 'Je ne suis expert qu'en plante veillez reposez une question' "
                    "et ne rien répondre d'autre. "
                    "Tu ne réponds à la query entre triple simple quote qu'avec les 5 informations données par le RAG si les informations sont présentes "
                    "et vérifie que ce soit bien la bonne plante. "
                    "Si l'information demandée n'est pas dans la liste, dire seulement 'désolé je ne sais pas' et ne continue pas. "
                    "Sinon, fais 2 petits paragraphes."
                )
            },
            {
                "role": "user",
                "content": query_final,
            },
        ]
    )