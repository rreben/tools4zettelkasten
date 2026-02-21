# rag.py
# Copyright (c) 2024 Dr. Rupert Rebentisch
# Licensed under the MIT license

import re
import hashlib
import logging
import os
from dataclasses import dataclass, field
from . import handle_filenames as hf
from . import settings as st
from .persistency import PersistencyManager

logger = logging.getLogger(__name__)

# Suppress noisy debug logs from third-party libraries
for _lib in ('chromadb', 'urllib3', 'sentence_transformers', 'httpx',
             'httpcore', 'openai', 'posthog'):
    logging.getLogger(_lib).setLevel(logging.WARNING)


SYSTEM_PROMPT = (
    "Du bist ein Assistent, der Fragen basierend auf einem persönlichen "
    "Zettelkasten beantwortet. Dir werden relevante Zettel (Notizen) als "
    "Kontext bereitgestellt.\n\n"
    "Regeln:\n"
    "- Antworte ausschließlich basierend auf den bereitgestellten Zetteln.\n"
    "- Wenn die Zettel keine Antwort auf die Frage hergeben, sage das "
    "ehrlich.\n"
    "- Verweise auf die Quell-Zettel mit deren ID und Titel.\n"
    "- Antworte in der Sprache der Frage (Deutsch oder Englisch).\n"
    "- Berücksichtige den bisherigen Konversationsverlauf bei Folgefragen."
)


@dataclass
class SearchResult:
    zettel_id: str
    title: str
    ordering: str
    filename: str
    content: str
    score: float


@dataclass
class SyncResult:
    added: int = 0
    updated: int = 0
    deleted: int = 0
    unchanged: int = 0
    metadata_updated: int = 0


def normalize_content(content: str) -> str:
    """Normalize markdown content by replacing link filenames with their IDs.

    This ensures that a reorganize (which changes orderings in filenames
    but not IDs) does not change the content hash.

    :param content: raw markdown content
    :return: normalized content with link targets replaced by IDs
    """
    def replace_link(match):
        description = match.group(1)
        filename = match.group(2)
        components = hf.get_filename_components(filename)
        zettel_id = components[2]
        if zettel_id:
            return f'[{description}]({zettel_id})'
        return match.group(0)

    return re.sub(
        r'\[([^\]]*)\]\(([a-zA-Z0-9_]*\.md)\)',
        replace_link,
        content
    )


def compute_content_hash(content: str) -> str:
    """Compute SHA-256 hash over normalized content.

    :param content: raw markdown content (will be normalized before hashing)
    :return: hex digest of the hash
    """
    normalized = normalize_content(content)
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


def _extract_title(content: str) -> str:
    """Extract the title from a markdown file (first # heading)."""
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('# '):
            return line[2:].strip()
    return ''


class ZettelkastenEmbedder:
    """Wrapper around sentence-transformers for embedding zettel content."""

    def __init__(self, model_name: str = None):
        if model_name is None:
            model_name = st.EMBEDDING_MODEL
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "sentence-transformers is required for RAG. "
                "Install with: pip install 'tools4zettelkasten[rag]'"
            )
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, documents: list) -> list:
        embeddings = self.model.encode(documents, show_progress_bar=False)
        return [e.tolist() for e in embeddings]

    def embed_query(self, query: str) -> list:
        embedding = self.model.encode([query], show_progress_bar=False)
        return embedding[0].tolist()


class VectorStore:
    """ChromaDB-backed vector store for zettelkasten notes."""

    def __init__(self, chroma_path: str = None, embedder=None):
        if chroma_path is None:
            chroma_path = st.CHROMA_DB_PATH
        try:
            import chromadb
        except ImportError:
            raise ImportError(
                "chromadb is required for RAG. "
                "Install with: pip install 'tools4zettelkasten[rag]'"
            )
        os.makedirs(chroma_path, exist_ok=True)
        self._client = chromadb.PersistentClient(path=chroma_path)
        self._embedder = embedder or ZettelkastenEmbedder()
        self._collection = self._client.get_or_create_collection(
            name='zettelkasten',
            metadata={'hnsw:space': 'cosine'}
        )

    def sync(self, persistency_manager: PersistencyManager,
             progress_callback=None) -> SyncResult:
        """Incrementally sync zettelkasten files into the vector database.

        - New files are added
        - Changed files (different content hash) are updated
        - Deleted files are removed
        - Metadata (filename, ordering) is always updated

        :param progress_callback: Optional callback(phase, current, total)
            for reporting progress to the caller.
        """
        def _progress(phase, current, total):
            if progress_callback:
                progress_callback(phase, current, total)

        result = SyncResult()
        filenames = persistency_manager.get_list_of_filenames()
        md_files = [f for f in filenames if f.endswith('.md')]

        # Build current state from filesystem
        current_zettel = {}
        total_files = len(md_files)
        for i, filename in enumerate(md_files):
            _progress('Reading files', i + 1, total_files)
            components = hf.get_filename_components(filename)
            zettel_id = components[2]
            if not zettel_id:
                continue
            content = persistency_manager.get_string_from_file_content(
                filename)
            current_zettel[zettel_id] = {
                'filename': filename,
                'ordering': components[0],
                'title': _extract_title(content),
                'content': content,
                'content_hash': compute_content_hash(content),
            }

        # Get existing state from ChromaDB
        existing_ids = set()
        existing_hashes = {}
        existing_meta = {}
        if self._collection.count() > 0:
            all_docs = self._collection.get(
                include=['metadatas']
            )
            for i, doc_id in enumerate(all_docs['ids']):
                existing_ids.add(doc_id)
                meta = all_docs['metadatas'][i]
                existing_hashes[doc_id] = meta.get('content_hash', '')
                existing_meta[doc_id] = meta

        current_ids = set(current_zettel.keys())

        # Determine what to add, update, delete
        to_add = current_ids - existing_ids
        to_delete = existing_ids - current_ids
        to_check = current_ids & existing_ids

        # Delete removed zettel
        if to_delete:
            self._collection.delete(ids=list(to_delete))
            result.deleted = len(to_delete)

        # Add new zettel
        if to_add:
            _progress('Embedding new zettel', 0, len(to_add))
            add_ids = list(to_add)
            add_docs = [current_zettel[zid]['content'] for zid in add_ids]
            add_metas = [
                {
                    'filename': current_zettel[zid]['filename'],
                    'ordering': current_zettel[zid]['ordering'],
                    'title': current_zettel[zid]['title'],
                    'content_hash': current_zettel[zid]['content_hash'],
                }
                for zid in add_ids
            ]
            add_embeddings = self._embedder.embed_documents(add_docs)
            _progress('Embedding new zettel', len(to_add), len(to_add))
            self._collection.add(
                ids=add_ids,
                documents=add_docs,
                metadatas=add_metas,
                embeddings=add_embeddings,
            )
            result.added = len(to_add)

        # Check existing zettel for content changes or metadata changes
        to_update_ids = []
        to_update_docs = []
        to_update_metas = []
        to_update_embeddings = []
        metadata_only_ids = []
        metadata_only_metas = []

        total_check = len(to_check)
        for i, zid in enumerate(to_check):
            _progress('Checking changes', i + 1, total_check)
            current = current_zettel[zid]
            old_hash = existing_hashes.get(zid, '')
            new_hash = current['content_hash']
            new_meta = {
                'filename': current['filename'],
                'ordering': current['ordering'],
                'title': current['title'],
                'content_hash': new_hash,
            }

            if new_hash != old_hash:
                # Content changed — re-embed
                to_update_ids.append(zid)
                to_update_docs.append(current['content'])
                to_update_metas.append(new_meta)
            else:
                # Content unchanged — check metadata
                old_meta = existing_meta.get(zid, {})
                if (old_meta.get('filename') != current['filename']
                        or old_meta.get('ordering') != current['ordering']
                        or old_meta.get('title') != current['title']):
                    metadata_only_ids.append(zid)
                    metadata_only_metas.append(new_meta)
                else:
                    result.unchanged += 1

        # Apply content updates (with new embeddings)
        if to_update_ids:
            _progress('Embedding updates', 0, len(to_update_ids))
            to_update_embeddings = self._embedder.embed_documents(
                to_update_docs)
            _progress('Embedding updates', len(to_update_ids),
                      len(to_update_ids))
            self._collection.update(
                ids=to_update_ids,
                documents=to_update_docs,
                metadatas=to_update_metas,
                embeddings=to_update_embeddings,
            )
            result.updated = len(to_update_ids)

        # Apply metadata-only updates (no re-embedding)
        if metadata_only_ids:
            self._collection.update(
                ids=metadata_only_ids,
                metadatas=metadata_only_metas,
            )
            result.metadata_updated = len(metadata_only_ids)

        return result

    def search(self, query: str, top_k: int = None) -> list:
        """Search for zettel similar to the query.

        :param query: search query text
        :param top_k: number of results to return
        :return: list of SearchResult objects
        """
        if top_k is None:
            top_k = int(st.RAG_TOP_K)

        if self._collection.count() == 0:
            return []

        top_k = min(top_k, self._collection.count())
        query_embedding = self._embedder.embed_query(query)
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=['documents', 'metadatas', 'distances'],
        )

        search_results = []
        for i in range(len(results['ids'][0])):
            meta = results['metadatas'][0][i]
            search_results.append(SearchResult(
                zettel_id=results['ids'][0][i],
                title=meta.get('title', ''),
                ordering=meta.get('ordering', ''),
                filename=meta.get('filename', ''),
                content=results['documents'][0][i],
                score=1.0 - results['distances'][0][i],
            ))
        return search_results

    def get_stats(self) -> dict:
        """Return statistics about the vector database."""
        return {
            'total_documents': self._collection.count(),
            'chroma_path': st.CHROMA_DB_PATH,
            'embedding_model': st.EMBEDDING_MODEL,
        }


def format_context(search_results: list) -> str:
    """Format search results as context for the LLM prompt."""
    parts = []
    for i, result in enumerate(search_results, 1):
        parts.append(
            f"[{i}] ID: {result.zettel_id} | "
            f"Titel: {result.title} | "
            f"Ordering: {result.ordering}\n"
            f"{result.content}"
        )
    return '\n\n'.join(parts)


def chat_completion(
    query: str,
    search_results: list,
    conversation_history: list = None,
) -> str:
    """Send a query with RAG context to the OpenAI API.

    :param query: user question
    :param search_results: relevant zettel from vector search
    :param conversation_history: list of previous messages
           [{'role': 'user', 'content': ...}, {'role': 'assistant', ...}]
    :return: assistant response text
    """
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError(
            "openai is required for RAG chat. "
            "Install with: pip install 'tools4zettelkasten[rag]'"
        )

    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY environment variable is not set. "
            "Please set it to your OpenAI API key."
        )

    client = OpenAI(api_key=api_key)
    context = format_context(search_results)

    messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]

    if conversation_history:
        messages.extend(conversation_history)

    user_message = (
        f"Kontext aus dem Zettelkasten:\n\n{context}\n\n"
        f"Frage: {query}"
    )
    messages.append({'role': 'user', 'content': user_message})

    response = client.chat.completions.create(
        model=st.LLM_MODEL,
        messages=messages,
    )

    return response.choices[0].message.content
