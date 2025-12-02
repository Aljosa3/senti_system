"""
Retrieval Connector for SENTI OS FAZA 16

This module provides secure access to internal documents and memory:
- Document retrieval from internal storage
- Memory access without exposing PII
- Context-aware information retrieval
- Privacy-preserving data access
- Integration with SENTI OS memory systems

All operations respect privacy boundaries and never expose sensitive data.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentType(Enum):
    """Types of documents that can be retrieved."""
    TEXT = "text"
    JSON = "json"
    LOG = "log"
    CONFIGURATION = "configuration"
    MEMORY = "memory"


class AccessLevel(Enum):
    """Access levels for document retrieval."""
    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"
    PRIVATE = "private"


@dataclass
class Document:
    """Represents a retrieved document."""
    document_id: str
    document_type: DocumentType
    content: str
    access_level: AccessLevel
    source_path: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    sanitized: bool = False


@dataclass
class RetrievalQuery:
    """Query for document retrieval."""
    query_text: str
    document_types: List[DocumentType] = field(default_factory=list)
    max_results: int = 10
    include_metadata: bool = True
    sanitize_pii: bool = True


@dataclass
class RetrievalResult:
    """Result of document retrieval."""
    query: str
    documents: List[Document]
    total_found: int
    filtered_count: int
    warnings: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class RetrievalConnector:
    """
    Secure connector for retrieving internal documents in SENTI OS.

    This connector provides privacy-preserving access to internal
    documents and memory, ensuring no PII or sensitive data is exposed.
    """

    SENSITIVE_PATTERNS = [
        r'\b\d{3}-\d{2}-\d{4}\b',
        r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    ]

    SENSITIVE_KEYWORDS = [
        "password", "secret", "api_key", "token", "credential",
        "private_key", "ssn", "credit_card",
    ]

    def __init__(self, base_path: str = "/home/pisarna/senti_system"):
        """
        Initialize the retrieval connector.

        Args:
            base_path: Base path for document retrieval
        """
        self.base_path = base_path
        self.allowed_paths = [
            os.path.join(base_path, "docs"),
            os.path.join(base_path, "memory_store"),
            os.path.join(base_path, "logs"),
        ]
        self.document_cache: Dict[str, Document] = {}
        self.access_log: List[Dict] = []

        logger.info("Retrieval Connector initialized")

    def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        """
        Retrieve documents based on query.

        Args:
            query: RetrievalQuery with search parameters

        Returns:
            RetrievalResult with matching documents
        """
        documents = []
        total_found = 0
        filtered_count = 0
        warnings = []

        for allowed_path in self.allowed_paths:
            if not os.path.exists(allowed_path):
                warnings.append(f"Path does not exist: {allowed_path}")
                continue

            path_docs, path_total, path_filtered = self._search_path(
                allowed_path,
                query,
            )

            documents.extend(path_docs)
            total_found += path_total
            filtered_count += path_filtered

        documents = documents[:query.max_results]

        self._log_access(query.query_text, len(documents))

        logger.info(f"Retrieval complete: {len(documents)} documents returned")

        return RetrievalResult(
            query=query.query_text,
            documents=documents,
            total_found=total_found,
            filtered_count=filtered_count,
            warnings=warnings,
        )

    def _search_path(
        self,
        path: str,
        query: RetrievalQuery,
    ) -> tuple[List[Document], int, int]:
        """
        Search a specific path for documents.

        Args:
            path: Path to search
            query: RetrievalQuery

        Returns:
            Tuple of (documents, total_found, filtered_count)
        """
        documents = []
        total_found = 0
        filtered_count = 0

        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    if not self._is_allowed_file(file):
                        continue

                    file_path = os.path.join(root, file)

                    if self._matches_query(file, query):
                        total_found += 1

                        doc = self._load_document(file_path, query)

                        if doc:
                            if self._passes_security_checks(doc):
                                documents.append(doc)
                            else:
                                filtered_count += 1

        except Exception as e:
            logger.error(f"Error searching path {path}: {e}")

        return documents, total_found, filtered_count

    def _is_allowed_file(self, filename: str) -> bool:
        """
        Check if file is allowed for retrieval.

        Args:
            filename: Name of file

        Returns:
            True if allowed, False otherwise
        """
        allowed_extensions = {
            ".txt", ".md", ".json", ".log", ".yaml", ".yml"
        }

        blocked_files = {
            "api_keys.conf", "secrets.json", "credentials.txt",
            ".env", ".ssh", "id_rsa", "id_dsa"
        }

        if filename in blocked_files:
            return False

        _, ext = os.path.splitext(filename)
        return ext.lower() in allowed_extensions

    def _matches_query(self, filename: str, query: RetrievalQuery) -> bool:
        """
        Check if filename matches query.

        Args:
            filename: Name of file
            query: RetrievalQuery

        Returns:
            True if matches, False otherwise
        """
        query_lower = query.query_text.lower()
        filename_lower = filename.lower()

        if query_lower in filename_lower:
            return True

        return False

    def _load_document(
        self,
        file_path: str,
        query: RetrievalQuery,
    ) -> Optional[Document]:
        """
        Load a document from file system.

        Args:
            file_path: Path to document
            query: RetrievalQuery

        Returns:
            Document instance or None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            doc_type = self._determine_document_type(file_path)

            doc = Document(
                document_id=os.path.basename(file_path),
                document_type=doc_type,
                content=content,
                access_level=self._determine_access_level(file_path),
                source_path=file_path,
                sanitized=False,
            )

            if query.sanitize_pii:
                doc = self._sanitize_document(doc)

            return doc

        except Exception as e:
            logger.error(f"Error loading document {file_path}: {e}")
            return None

    def _determine_document_type(self, file_path: str) -> DocumentType:
        """
        Determine document type from file path.

        Args:
            file_path: Path to file

        Returns:
            DocumentType
        """
        _, ext = os.path.splitext(file_path)

        type_map = {
            ".json": DocumentType.JSON,
            ".log": DocumentType.LOG,
            ".yaml": DocumentType.CONFIGURATION,
            ".yml": DocumentType.CONFIGURATION,
        }

        return type_map.get(ext.lower(), DocumentType.TEXT)

    def _determine_access_level(self, file_path: str) -> AccessLevel:
        """
        Determine access level for document.

        Args:
            file_path: Path to file

        Returns:
            AccessLevel
        """
        if "docs" in file_path:
            return AccessLevel.PUBLIC

        if "memory_store" in file_path:
            return AccessLevel.INTERNAL

        if "logs" in file_path:
            return AccessLevel.INTERNAL

        return AccessLevel.RESTRICTED

    def _passes_security_checks(self, doc: Document) -> bool:
        """
        Check if document passes security checks.

        Args:
            doc: Document to check

        Returns:
            True if passes, False otherwise
        """
        if doc.access_level == AccessLevel.PRIVATE:
            return False

        content_lower = doc.content.lower()

        for keyword in self.SENSITIVE_KEYWORDS:
            if keyword in content_lower and not doc.sanitized:
                logger.warning(f"Document {doc.document_id} contains sensitive keyword")
                return False

        return True

    def _sanitize_document(self, doc: Document) -> Document:
        """
        Sanitize document to remove PII.

        Args:
            doc: Document to sanitize

        Returns:
            Sanitized Document
        """
        import re

        sanitized_content = doc.content

        for pattern in self.SENSITIVE_PATTERNS:
            sanitized_content = re.sub(pattern, "[REDACTED]", sanitized_content)

        for keyword in self.SENSITIVE_KEYWORDS:
            pattern = rf'\b{keyword}\s*[:=]\s*\S+'
            sanitized_content = re.sub(
                pattern,
                f"{keyword}: [REDACTED]",
                sanitized_content,
                flags=re.IGNORECASE,
            )

        doc.content = sanitized_content
        doc.sanitized = True

        return doc

    def _log_access(self, query: str, results_count: int) -> None:
        """
        Log document access for audit trail.

        Args:
            query: Query text
            results_count: Number of results returned
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "results_count": results_count,
        }

        self.access_log.append(log_entry)

        if len(self.access_log) > 1000:
            self.access_log = self.access_log[-1000:]

    def get_document_by_id(self, document_id: str) -> Optional[Document]:
        """
        Retrieve a specific document by ID.

        Args:
            document_id: Document identifier

        Returns:
            Document if found, None otherwise
        """
        if document_id in self.document_cache:
            return self.document_cache[document_id]

        for allowed_path in self.allowed_paths:
            if not os.path.exists(allowed_path):
                continue

            for root, dirs, files in os.walk(allowed_path):
                if document_id in files:
                    file_path = os.path.join(root, document_id)
                    query = RetrievalQuery(
                        query_text=document_id,
                        sanitize_pii=True,
                    )
                    doc = self._load_document(file_path, query)

                    if doc:
                        self.document_cache[document_id] = doc
                        return doc

        return None

    def get_memory_entries(
        self,
        limit: int = 10,
        sanitize: bool = True,
    ) -> List[Document]:
        """
        Retrieve recent memory entries.

        Args:
            limit: Maximum number of entries to return
            sanitize: Whether to sanitize PII

        Returns:
            List of Document instances
        """
        memory_path = os.path.join(self.base_path, "memory_store")

        if not os.path.exists(memory_path):
            logger.warning("Memory store path does not exist")
            return []

        documents = []

        try:
            files = sorted(
                [
                    os.path.join(memory_path, f)
                    for f in os.listdir(memory_path)
                    if f.endswith('.json')
                ],
                key=lambda x: os.path.getmtime(x),
                reverse=True,
            )

            for file_path in files[:limit]:
                query = RetrievalQuery(
                    query_text="",
                    sanitize_pii=sanitize,
                )
                doc = self._load_document(file_path, query)

                if doc:
                    documents.append(doc)

        except Exception as e:
            logger.error(f"Error retrieving memory entries: {e}")

        return documents

    def get_statistics(self) -> Dict:
        """
        Get retrieval statistics.

        Returns:
            Dictionary with statistics
        """
        total_accesses = len(self.access_log)

        if total_accesses == 0:
            return {
                "total_accesses": 0,
                "cached_documents": len(self.document_cache),
            }

        recent_queries = [
            entry["query"]
            for entry in self.access_log[-10:]
        ]

        avg_results = sum(
            entry["results_count"] for entry in self.access_log
        ) / total_accesses

        return {
            "total_accesses": total_accesses,
            "cached_documents": len(self.document_cache),
            "average_results": round(avg_results, 2),
            "recent_queries": recent_queries,
        }


def create_connector(base_path: str = "/home/pisarna/senti_system") -> RetrievalConnector:
    """
    Create and return a retrieval connector.

    Args:
        base_path: Base path for document retrieval

    Returns:
        Configured RetrievalConnector instance
    """
    connector = RetrievalConnector(base_path)
    logger.info("Retrieval Connector created")
    return connector
