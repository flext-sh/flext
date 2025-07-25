#!/usr/bin/env python3
"""Teste de compatibilidade do Gensim com Python 3.13 e NumPy 2.0.

Este módulo testa a integração do gensim forkado com o projeto flext,
validando compatibilidade com Python 3.13 e NumPy 2.0.
"""

import os
import sys
import tempfile
import time

import numpy as np
import pytest
from gensim.models import Word2Vec


class TestGensimCompatibility:
    """Testes de compatibilidade do Gensim com Python 3.13 e NumPy 2.0."""

    def test_imports(self) -> None:
        """Teste de imports básicos."""
        import gensim

        assert gensim.__version__ is not None
        assert np.__version__ >= "2.0.0"
        assert sys.version_info >= (3, 13)

    def test_word2vec(self) -> None:
        """Teste do modelo Word2Vec."""
        from gensim.models import Word2Vec
        from gensim.test.utils import common_texts

        start_time = time.time()
        model = Word2Vec(sentences=common_texts, vector_size=100, window=5, min_count=1, workers=1)
        training_time = time.time() - start_time

        assert len(model.wv.key_to_index) > 0
        assert training_time < 10.0  # Deve ser rápido
        assert model.vector_size == 100

        # Teste de acesso aos vetores
        vocab = list(model.wv.key_to_index.keys())
        assert len(vocab) > 0
        vector = model.wv[vocab[0]]
        assert len(vector) == 100

    def test_doc2vec(self) -> None:
        """Teste do modelo Doc2Vec."""
        from gensim.models.doc2vec import Doc2Vec, TaggedDocument
        from gensim.test.utils import common_texts

        documents = [TaggedDocument(doc, [i]) for i, doc in enumerate(common_texts)]
        model = Doc2Vec(documents, vector_size=100, window=5, min_count=1, workers=1, epochs=10)

        assert len(model.dv) > 0
        doc_vector = model.dv[0]
        assert len(doc_vector) == 100

    def test_lda(self) -> None:
        """Teste do modelo LDA."""
        from gensim.corpora import Dictionary
        from gensim.models import LdaModel
        from gensim.test.utils import common_texts

        dictionary = Dictionary(common_texts)
        corpus = [dictionary.doc2bow(text) for text in common_texts]
        model = LdaModel(corpus, num_topics=3, id2word=dictionary, passes=10)

        assert model.num_topics == 3
        topic_words = model.show_topic(0, 3)
        assert len(topic_words) == 3

    def test_tfidf(self) -> None:
        """Teste do modelo TF-IDF."""
        from gensim.corpora import Dictionary
        from gensim.models import TfidfModel
        from gensim.test.utils import common_texts

        dictionary = Dictionary(common_texts)
        corpus = [dictionary.doc2bow(text) for text in common_texts]
        model = TfidfModel(corpus)

        assert len(dictionary) > 0
        tfidf_doc = model[corpus[0]]
        assert len(tfidf_doc) > 0

    def test_similarity(self) -> None:
        """Teste de similaridade."""
        from gensim.corpora import Dictionary
        from gensim.models import TfidfModel
        from gensim.similarities import SparseMatrixSimilarity
        from gensim.test.utils import common_texts

        dictionary = Dictionary(common_texts)
        corpus = [dictionary.doc2bow(text) for text in common_texts]
        tfidf = TfidfModel(corpus)
        corpus_tfidf = tfidf[corpus]
        index = SparseMatrixSimilarity(corpus_tfidf, num_features=len(dictionary))

        similarity_score = index[corpus_tfidf[0]][1]
        assert 0 <= similarity_score <= 1

    def test_numpy_compatibility(self) -> None:
        """Teste de compatibilidade com NumPy 2.0."""
        from gensim.models import Word2Vec
        from gensim.test.utils import common_texts

        model = Word2Vec(sentences=common_texts, vector_size=100, window=5, min_count=1, workers=1)

        vector1 = model.wv["computer"]
        vector2 = model.wv["system"]

        # Operações NumPy
        dot_product = np.dot(vector1, vector2)
        cosine_sim = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
        euclidean_dist = np.linalg.norm(vector1 - vector2)

        assert isinstance(dot_product, (float, np.floating))
        assert isinstance(cosine_sim, (float, np.floating))
        assert isinstance(euclidean_dist, (float, np.floating))
        assert 0 <= cosine_sim <= 1

    def test_serialization(self) -> None:
        """Teste de serialização."""
        from gensim.models import Word2Vec
        from gensim.test.utils import common_texts

        model = Word2Vec(sentences=common_texts, vector_size=100, window=5, min_count=1, workers=1)
        original_vocab_size = len(model.wv.key_to_index)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".model") as tmp:
            model.save(tmp.name)
            loaded_model = Word2Vec.load(tmp.name)
            loaded_vocab_size = len(loaded_model.wv.key_to_index)
            os.unlink(tmp.name)

        assert original_vocab_size == loaded_vocab_size
        assert model.vector_size == loaded_model.vector_size

    def test_performance(self) -> None:
        """Teste de performance."""
        from gensim.models import Word2Vec
        from gensim.test.utils import common_texts

        start_time = time.time()
        model = Word2Vec(
            sentences=common_texts * 100,
            vector_size=100,
            window=5,
            min_count=1,
            workers=1,
        )
        training_time = time.time() - start_time

        assert training_time < 30.0  # Deve ser rápido
        assert len(model.wv.key_to_index) > 0

    def test_flext_integration(self) -> None:
        """Teste de integração com o projeto flext."""
        from gensim.models import Word2Vec
        from gensim.test.utils import common_texts

        # Simular uso do gensim em um contexto do flext
        model = Word2Vec(sentences=common_texts, vector_size=50, window=3, min_count=1, workers=1)

        assert len(model.wv.key_to_index) > 0
        assert model.vector_size == 50
        assert len(list(model.wv.key_to_index.keys())) > 0


class TestGensimVersions:
    """Testes de versões e compatibilidade."""

    def test_python_version(self) -> None:
        """Teste da versão do Python."""
        assert sys.version_info >= (3, 13)

    def test_numpy_version(self) -> None:
        """Teste da versão do NumPy."""
        assert np.__version__ >= "2.0.0"

    def test_gensim_version(self) -> None:
        """Teste da versão do Gensim."""
        import gensim

        assert gensim.__version__ is not None


@pytest.fixture
def gensim_model() -> Word2Vec:
    """Fixture para criar um modelo Word2Vec para testes."""
    from gensim.models import Word2Vec
    from gensim.test.utils import common_texts

    return Word2Vec(sentences=common_texts, vector_size=50, window=3, min_count=1, workers=1)


def test_gensim_fixture(gensim_model: Word2Vec) -> None:
    """Teste usando fixture do gensim."""
    assert len(gensim_model.wv.key_to_index) > 0
    assert gensim_model.vector_size == 50
