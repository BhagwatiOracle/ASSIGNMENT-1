import os
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from langchain_groq import ChatGroq

from langchain_core.prompts import ChatPromptTemplate


load_dotenv()


# --------------------------------------------------
# 1. LOAD DOCUMENTS
# --------------------------------------------------

files = [
    "ai-2-data/policy_master_v1.md",
    "ai-2-data/circular_2026_08_amendment.md",
    "ai-2-data/merchant_faq_2026-03.md"
]


documents = []

for file in files:

    loader = TextLoader(
        file,
        encoding="utf-8"
    )

    docs = loader.load()

    # Store filename for citation
    for doc in docs:
        doc.metadata["source"] = file

    documents.extend(docs)


# --------------------------------------------------
# 2. SPLIT DOCUMENTS
# --------------------------------------------------

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100
)

chunks = splitter.split_documents(documents)


# --------------------------------------------------
# 3. HUGGING FACE EMBEDDINGS
# --------------------------------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# --------------------------------------------------
# 4. CREATE VECTOR DATABASE
# --------------------------------------------------

vectorstore = FAISS.from_documents(
    chunks,
    embeddings
)


retriever = vectorstore.as_retriever(
    search_kwargs={"k": 4}
)



# GRAQ LLM

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)


# --------------------------------------------------
# 6. PROMPT
# --------------------------------------------------

prompt = ChatPromptTemplate.from_template("""
You are a merchant policy assistant.

Answer the question ONLY using the provided policy documents.

Important rules:

1. Do not invent information.
2. Do not invent clause numbers.
3. If the answer is not present, say CANNOT_ANSWER.
4. Pay attention to the policy date.
5. If two documents disagree, explain the conflict.
6. Be concise.

Policy date:
{date}

Policy documents:
{context}

Question:
{question}

Answer:
""")



# ASK FUNCTION


def ask(question, as_of_date="2026-08-15"):

    # Retrieve relevant chunks
    docs = retriever.invoke(question)

    # Build context
    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    # Ask Groq
    chain = prompt | llm

    response = chain.invoke({
        "question": question,
        "date": as_of_date,
        "context": context
    })

    # Create citations
    citations = []

    for doc in docs:

        source = doc.metadata.get(
            "source",
            "Unknown"
        )

        citations.append(source)

    return {
        "answer": response.content,
        "citations": list(set(citations)),
        "status": "ANSWERED"
    }


# --------------------------------------------------
# 8. TEST
# --------------------------------------------------

if __name__ == "__main__":

    result = ask(
        "When does a small merchant receive UPI money?",
        "2026-08-15"
    )

    print("\nANSWER:")
    print(result["answer"])

    print("\nCITATIONS:")

    for citation in result["citations"]:
        print("-", citation)

    print("\nSTATUS:")
    print(result["status"])