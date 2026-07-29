import os
import datetime
from groq import Groq
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import numpy as np
from pathlib import Path
import faiss
import pickle

load_dotenv()


class VectorStore:
    def __init__(self, index_file="faiss_index.bin", meta_file="metadata.pkl"):
        self.documents = []
        self.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index_file = Path(index_file)
        self.meta_file = Path(meta_file)

    def _get_embeddings(self, text: str):
        embedding = self.model.encode(text, convert_to_numpy=True).astype("float32")   # Отримуємо вектор у форматі float32 з правильними розмірностями (1, dimension)
        embedding = np.expand_dims(embedding, axis=0)

        faiss.normalize_L2(embedding)  # Нормалізуємо vector для L2/Cosine similarity
        return embedding

    def add_text(self, text: str, metadata: dict = None):
        doc_id = len(self.documents)

        vector = self._get_embeddings(text)
        self.index.add(vector)

        self.documents.append({
            "id": doc_id,
            "text": text,
            "metadata": metadata,
        })
        return doc_id

    def search(self, query: str, top_n: int = 3):
        if not self.documents:
            return []

        query_vector = self._get_embeddings(query)

        scores, indices = self.index.search(query_vector, top_n)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1 and idx < len(self.documents):  # Перевірка на випадок порожніх результатів
                results.append({
                    "document": self.documents[idx],
                    "score": float(score)
                })

        return results

    def save(self):
        """Збереження індексу FAISS та метаданих на диск"""
        faiss.write_index(self.index, str(self.index_file))
        with open(self.meta_file, "wb") as f:
            pickle.dump(self.documents, f)
        print("Базу знань успішно збережено на диск!")

    def load(self) -> bool:
        """Завантаження індексу FAISS та метаданих з диска"""
        if self.index_file.exists() and self.meta_file.exists():
            self.index = faiss.read_index(str(self.index_file))
            with open(self.meta_file, "rb") as f:
                self.documents = pickle.load(f)
            return True
        return False

    def load_documents(self):
        if self.load():
            print(f" Завантажено існуючий FAISS індекс ({self.index.ntotal} документів) з диска.")
            return

        print(" Первинна індексація: генерація векторів та створення FAISS індексу...")
        target_dir = Path.cwd() / "quantum_corpus"

        if target_dir.is_dir():
            for file_path in target_dir.iterdir():
                if file_path.is_file() and file_path.suffix in [".md", ".txt"]:
                    self.add_text(
                        text=file_path.read_text(encoding="utf-8"),
                        metadata={"source": file_path.name}
                    )
            self.save()

    def get_by_id(self, doc_id: int):
        for document in self.documents:
            if document["id"] == doc_id:
                return document
        return None


class GroqChatSession:
    def __init__(self):
        self.API_KEY = os.getenv("API_KEY")
        self.client = Groq(api_key=self.API_KEY)
        self.model = "llama-3.1-8b-instant"
        self.default_prompt = "You are a helpful educational assistant. Answer questions based ONLY on the provided context documents. Always mention which source file the information came from. Respond in Ukrainian.\n\n"

    def _build_prompt(self, query: str, context_documents: list):
        formatted_docs = []
        for doc in context_documents:
            source = doc["document"]["metadata"].get("source", "Невідомо")
            text = doc["document"]["text"]
            formatted_docs.append(f"[Джерело: {source}]\n{text}")

        context_text = "\n\n".join(formatted_docs)

        system_content = (
            f"{self.default_prompt}Контекст з бази знань:\n{context_text}"
        )

        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": query}
        ]

    def _call_ai(self, messages: list):
        response = self.client.chat.completions.create(model=self.model, messages=messages)
        return response

    def get_response(self, query: str, context_documents: list):
        messages = self._build_prompt(query=query, context_documents=context_documents)

        ai_response = self._call_ai(messages=messages)

        return ai_response.choices[0].message.content


def log_interactions(query: str, response: str, matches: list):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logs_dir = Path.cwd() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    file_path = logs_dir / "logs.md"

    logs_entry = f"Timestamp: {timestamp}, Query: {query}, Response: {response}\n"

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(logs_entry)

def main():
    print("Завантаження бази знань...")
    store = VectorStore()
    store.load_documents()

    if not store.documents:
        print(" Увага: База знань порожня! Перевірте папку 'quantum_corpus'.")
        return

    chat = GroqChatSession()

    print("\n" + "=" * 50)
    print(" Чат з базою знань готовий! Введіть 'exit' або 'quit' для виходу.")
    print("=" * 50 + "\n")

    while True:
        try:
            user_query = input("> You: ").strip()

            if user_query.lower() in ["exit", "quit", "вихід", "q"]:
                print("\n До зустрічі!")
                break

            if not user_query:
                continue

            matches = store.search(query=user_query, top_n=3)

            print("\n-> Top 3 Matches:")
            if matches:
                for i, match in enumerate(matches, 1):
                    snippet = match['document']['text'].replace('\n', ' ')[:80]
                    score = match['score']
                    print(f"[{i}] \"{snippet}...\" (Score: {score:.2f})")
            else:
                print("Нічого не знайдено.")

            ai_response = chat.get_response(query=user_query, context_documents=matches)

            print("\n-> Groq says:")
            print(ai_response)
            print("\n" + "-" * 50 + "\n")

            log_interactions(query=user_query, response=ai_response, matches=matches)

        except KeyboardInterrupt:
            print("\n\n Сесію перервано. До зустрічі!")
            break
        except Exception as e:
            print(f"\n Виникла помилка: {e}\n")


if __name__ == "__main__":
    main()