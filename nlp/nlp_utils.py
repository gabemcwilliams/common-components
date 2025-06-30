import pandas as pd
import spacy
from typing import List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer, SentiText


class NLPPrep:
    """
    A class for preprocessing text data for NLP tasks.

    This class provides methods for tokenizing, lemmatizing, removing stopwords,
    and other NLP tasks. It also includes functionality for creating feature matrices
    using CountVectorizer and TfidfVectorizer from the scikit-learn library.
    """

    def __init__(
            self,
            model: str = 'en_core_web_sm',
            lowercase: bool = True,
            remove_stopwords: bool = True,
            keep_pos: Optional[List[str]] = None
    ):
        """
        Initializes the NLP pipeline with configuration options.

        Args:
            model: spaCy model to load (default is 'en_core_web_sm').
            lowercase: Whether to lowercase tokens (default is True).
            remove_stopwords: Whether to filter out stopwords (default is True).
            keep_pos: Optional list of POS tags to keep (e.g., ['NOUN', 'VERB']).
        """
        self.model_name = model
        self.lowercase = lowercase
        self.remove_stopwords = remove_stopwords
        self.keep_pos = keep_pos

        self.__nlp = spacy.load(model)  # Load the spaCy model
        self.__stopwords = self.__nlp.Defaults.stop_words  # Get default stopwords from spaCy

    def preprocess(
            self,
            text: str,
            lowercase: Optional[bool] = None,
            remove_stopwords: Optional[bool] = None,
            keep_pos: Optional[List[str]] = None
    ) -> List[str]:
        """
        Main processing method. Applies lemmatization, case normalization,
        stopword removal, and optional POS filtering.

        Args:
            text: Input string to preprocess.
            lowercase: Override the default lowercase behavior (optional).
            remove_stopwords: Override the default stopword removal (optional).
            keep_pos: Override the default POS filtering (optional).

        Returns:
            List of processed tokens (strings).
        """
        doc = self.__nlp(text)

        # Apply overrides if provided
        lc = lowercase if lowercase is not None else self.lowercase
        rs = remove_stopwords if remove_stopwords is not None else self.remove_stopwords
        kp = keep_pos if keep_pos is not None else self.keep_pos

        tokens = []

        for token in doc:
            if token.is_punct or token.is_space:
                continue  # Skip punctuation and spaces
            if rs and token.text.lower() in self.__stopwords:
                continue  # Skip stopwords if removal is enabled
            if kp and token.pos_ not in kp:
                continue  # Skip tokens not matching the desired POS tags

            word = token.lemma_ if token.lemma_ != "-PRON-" else token.text
            if lc:
                word = word.lower()  # Lowercase the token if required

            tokens.append(word)

        return tokens

    def _tokenize(self, text: str) -> List[str]:
        """Internal method: Return raw tokens without filtering."""
        return [token.text for token in self.__nlp(text)]

    def _lemmatize(self, text: str) -> List[str]:
        """Internal method: Return lemmatized tokens without filtering."""
        return [token.lemma_ for token in self.__nlp(text)]

    def _get_pos_tags(self, text: str) -> List[tuple]:
        """Internal method: Return (token, POS tag) tuples."""
        return [(token.text, token.pos_) for token in self.__nlp(text)]

    def _get_entities(self, text: str) -> List[tuple]:
        """Internal method: Return (entity, label) tuples for named entities."""
        return [(ent.text, ent.label_) for ent in self.__nlp(text)]

    def _get_doc(self, text: str):
        """Internal method: Return raw spaCy Doc object."""
        return self.__nlp(text)

    def create_count_vectorizer_dataframe(
            self,
            text: pd.Series | List[List[str]],
            stop_words: str = 'english',
            ngram_range: tuple = (1, 2),
            min_df: float = 0.2
    ) -> pd.DataFrame:
        """
        Create a DataFrame from a CountVectorizer feature matrix.

        Args:
            text: A pandas Series or a list of token lists to vectorize.
            stop_words: Stopwords to filter out during vectorization.
            ngram_range: Tuple for the n-gram range (e.g., (1, 2) for unigrams and bigrams).
            min_df: Minimum document frequency for a term to be included.

        Returns:
            A pandas DataFrame with vectorized features.
        """
        # Confirm and convert token lists into strings
        if isinstance(text, pd.Series) or (isinstance(text, list) and isinstance(text[0], list)):
            print(f"[Vectorizer] Joining {len(text)} token lists into space-separated strings.")
        text = [' '.join(tokens) for tokens in text]

        count_vectorizer = CountVectorizer(
            stop_words=stop_words,
            ngram_range=ngram_range,
            min_df=min_df  # Only keep terms in at least 20% of docs
        )

        X = count_vectorizer.fit_transform(text)

        print(f"[Vectorizer] Feature matrix shape: {X.shape}")
        return pd.DataFrame(X.toarray(), columns=count_vectorizer.get_feature_names_out())

    def create_tfidf_vectorizer_dataframe(
            self,
            text: pd.Series | List[List[str]],
            stop_words: str = 'english',
            ngram_range: tuple = (1, 2),
            min_df: float = 0.2,
            max_df: float = 0.8
    ) -> pd.DataFrame:
        """
        Create a DataFrame from a TfidfVectorizer feature matrix.

        Args:
            text: A pandas Series or a list of token lists to vectorize.
            stop_words: Stopwords to filter out during vectorization.
            ngram_range: Tuple for the n-gram range (e.g., (1, 2) for unigrams and bigrams).
            min_df: Minimum document frequency for a term to be included.
            max_df: Maximum document frequency for a term to be included.

        Returns:
            A pandas DataFrame with vectorized features.

        """
        # Confirm and convert token lists into strings
        if isinstance(text, pd.Series) or (isinstance(text, list) and isinstance(text[0], list)):
            print(f"[Vectorizer] Joining {len(text)} token lists into space-separated strings.")
        text = [' '.join(tokens) for tokens in text]

        tfidf_vectorizer = TfidfVectorizer(
            stop_words=stop_words,
            ngram_range=ngram_range,
            min_df=min_df,  # Only keep terms in at least 20% of docs
            max_df=max_df,
        )

        X = tfidf_vectorizer.fit_transform(text)

        print(f"[Vectorizer] Feature matrix shape: {X.shape}")
        return pd.DataFrame(X.toarray(), columns=tfidf_vectorizer.get_feature_names_out())

    @staticmethod
    def sentiment_score(text: str, compound_only:bool=False) -> float:
        """Internal method: Return sentence score."""
        sid = SentimentIntensityAnalyzer()
        if compound_only:
            return sid.polarity_scores(text)['compound']
        return sid.polarity_scores(text)
