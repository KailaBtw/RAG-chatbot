# Genre Analysis of RuneScape Wiki: A Computational Approach to Understanding Gaming Encyclopedia Discourse

## Abstract

This project presents a comprehensive computational analysis of the RuneScape Wiki, examining it as a distinct genre of technical documentation within gaming communities. By combining traditional genre analysis methodologies with modern natural language processing techniques, this study investigates the structural, linguistic, and rhetorical characteristics of wiki articles. The project implements a Retrieval-Augmented Generation (RAG) system to enable interactive querying of the wiki corpus, demonstrating practical applications of NLP methods for information retrieval and question-answering. Through systematic analysis of 500+ wiki pages, this work reveals how gaming communities construct knowledge through standardized documentation formats, technical vocabulary, and collaborative editing practices.

## 1. Introduction and Project Scope

### 1.1 Project Overview

The RuneScape Wiki represents a unique corpus of technical documentation created and maintained by gaming communities. Unlike traditional encyclopedias or academic texts, gaming wikis serve as practical reference materials for players seeking specific information about game mechanics, items, quests, and strategies. This project examines the RuneScape Wiki as a distinct genre, analyzing its discourse patterns, structural conventions, and linguistic characteristics through computational methods.

The project encompasses two primary components: (1) a comprehensive genre analysis system that examines structural features, language patterns, and rhetorical moves in wiki articles, and (2) a functional RAG (Retrieval-Augmented Generation) chatbot that enables users to query the wiki corpus using natural language questions. This dual approach demonstrates both analytical and applied uses of NLP techniques covered in the course.

### 1.2 Research Questions

This project addresses several key questions:

1. What structural and linguistic patterns characterize RuneScape Wiki articles as a distinct genre?
2. How do gaming communities use specialized vocabulary and discourse conventions in technical documentation?
3. Can modern NLP techniques (embeddings, vector databases, RAG) effectively enable information retrieval from gaming wiki corpora?
4. What rhetorical moves and organizational strategies do wiki editors employ to structure information for player audiences?

### 1.3 Dataset Description

The dataset consists of 500+ randomly sampled pages from the RuneScape Wiki (runescape.wiki), collected via the MediaWiki API. Pages include articles about game items, locations, NPCs (non-player characters), quests, skills, and game mechanics. Each page contains raw wikitext markup, which includes structural elements (templates, sections, links) and content text. This corpus represents a unique and understudied domain of technical writing that combines gaming terminology with encyclopedia-style documentation.

The random sampling approach ensures diversity across article types, avoiding bias toward only the most popular pages. The dataset includes both short reference articles (e.g., item descriptions) and longer comprehensive guides (e.g., skill training methods), providing a representative sample of the wiki's content spectrum.

## 2. Methodology

### 2.1 Data Collection

Data collection was implemented through a custom MediaWiki API client (`wiki_api.py`) that interfaces with the RuneScape Wiki's public API. The collection process follows several key steps:

1. **Title Retrieval**: The system fetches random page titles using the MediaWiki `list=random` query, retrieving up to 500 unique titles per collection run.

2. **Content Extraction**: For each title, the system requests raw wikitext using the `action=parse&prop=wikitext` API endpoint. This preserves all structural markup (templates, links, sections) necessary for genre analysis.

3. **Rate Limiting and Error Handling**: The client implements exponential backoff retry logic and respects API rate limits (429 responses), with configurable delays between requests to maintain polite API usage.

4. **Data Persistence**: Collected pages are stored as JSON, with each entry containing the page title and full wikitext. The system supports incremental collection, avoiding duplicate fetches by maintaining a cache of previously collected pages.

The collection script (`main.py`) orchestrates this process using parallel processing (ThreadPoolExecutor) to improve efficiency while respecting rate limits through conservative worker counts.

### 2.2 Text Preprocessing

Preprocessing serves dual purposes: preparing text for embedding generation in the RAG system and extracting clean content for genre analysis. The preprocessing pipeline (`preprocess.py`) implements several transformations:

1. **Link Normalization**: Converts MediaWiki link syntax `[[link|display]]` to display text, preserving semantic content while removing markup.

2. **Template Removal**: Removes structural templates (e.g., `{{External|os}}`, `{{Disambig}}`) that serve organizational purposes but don't contribute to content analysis.

3. **File Reference Removal**: Strips image and file references (`[[File:...]]`) while preserving any associated alt text.

4. **Whitespace Normalization**: Collapses multiple spaces and newlines to improve text consistency for downstream processing.

The preprocessing strategy prioritizes content preservation over aggressive cleaning, ensuring that game-specific terminology and technical descriptions remain intact for both analysis and retrieval tasks.

### 2.3 Genre Analysis Methods

The genre analysis component (`genre_analyzer.py`) implements systematic examination across multiple dimensions:

#### 2.3.1 Structural Feature Analysis

The system extracts and analyzes structural patterns that characterize wiki articles:

- **Section Identification**: Uses regex patterns to identify section headers (`== Header ==`), counting frequency of common sections (e.g., "History", "Stats", "Requirements", "Trivia").

- **Template Analysis**: Identifies and counts MediaWiki templates (`{{Template}}`), which reveal standardized information structures (e.g., infoboxes for items, stat tables for equipment).

- **Page Length Metrics**: Calculates average word counts across the corpus to understand typical article length and information density.

These structural features reveal how wiki editors organize information consistently, creating predictable navigation patterns for readers.

#### 2.3.2 Language Pattern Analysis

Language analysis focuses on identifying game-specific vocabulary and technical terminology:

- **Word Frequency Analysis**: Generates frequency distributions of words across the corpus, filtering out common English stop words to highlight domain-specific terms.

- **Vocabulary Metrics**: Calculates vocabulary size (unique terms) and total word counts to quantify the specialized lexicon used in gaming documentation.

- **Game-Specific Term Extraction**: Identifies terms that appear frequently but are not common English words, revealing the technical vocabulary of the RuneScape gaming community.

This analysis demonstrates how gaming communities develop specialized lexicons that enable precise communication about game mechanics, items, and strategies.

#### 2.3.3 Rhetorical Move Identification

The system identifies common rhetorical moves—recurring communicative functions—in wiki articles:

- **Define Item**: Presence of infoboxes indicates definitional moves that establish what an item/entity is.

- **Provide Context**: Sections like "History" or "Background" provide contextual information.

- **Specify Mechanics**: Sections like "Stats" or "Requirements" detail game mechanics and technical specifications.

- **Add Interesting Details**: "Trivia" or "Notes" sections provide supplementary information.

- **Connect Related Content**: "See also" sections create intertextual connections.

- **Reference Other Sources**: External link templates indicate citation practices.

- **Show Visual Evidence**: "Gallery" sections demonstrate multimodal communication.

These moves reveal how wiki articles balance multiple communicative goals: providing quick reference information while also offering comprehensive context and interesting details.

#### 2.3.4 Slang and Community Terms Analysis

The system includes a comprehensive dictionary of RuneScape-specific slang terms and abbreviations, analyzing their frequency in the corpus. This includes:

- Game abbreviations (e.g., "osrs" for Old School RuneScape, "f2p" for free-to-play)
- Skill and gameplay terminology (e.g., "xp" for experience, "afk" for away from keyboard)
- Community-specific language (e.g., "ironman" for a game mode, "pk" for player killing)

This analysis reveals how gaming communities develop specialized language that may be opaque to outsiders but enables efficient communication among community members.

### 2.4 RAG System Implementation

The RAG (Retrieval-Augmented Generation) system demonstrates practical application of NLP techniques for information retrieval and question-answering:

#### 2.4.1 Embedding Generation

The system uses sentence transformers (`sentence-transformers/all-MiniLM-L6-v2`) to generate dense vector representations of wiki pages. This embedding model converts text into 384-dimensional vectors that capture semantic meaning, enabling similarity-based retrieval.

#### 2.4.2 Vector Database Indexing

Pages are indexed in ChromaDB, a vector database optimized for similarity search. The indexing process (`indexer.py`):

1. Loads collected wiki pages from JSON storage
2. Preprocesses wikitext to clean markup
3. Generates embeddings for each page using the sentence transformer model
4. Stores embeddings, documents, and metadata (title, URL) in ChromaDB

The system uses full-page chunks (one chunk per page) rather than splitting pages into smaller segments, which works well for the typically concise wiki articles.

#### 2.4.3 Retrieval and Generation

The RAG engine (`rag_engine.py`) implements the retrieval-augmented generation pipeline:

1. **Query Embedding**: User questions are embedded using the same sentence transformer model.

2. **Similarity Search**: ChromaDB retrieves the top-k most similar pages (default k=5) based on cosine similarity between query and document embeddings.

3. **Context Assembly**: Retrieved page content is assembled into a context string, with each page clearly delimited.

4. **Answer Generation**: The context and question are sent to Ollama (running Llama 3.1 8B locally) with a prompt instructing the model to answer based on the provided context.

5. **Source Attribution**: The system returns both the generated answer and source citations (page titles and URLs) for transparency.

The chatbot interface (`chatbot_cli.py`) provides an interactive command-line interface for querying the system, with optional debug mode showing retrieved context and processing details.

## 3. Key Findings and Analysis

### 3.1 Structural Characteristics

Analysis reveals highly standardized structural patterns across RuneScape Wiki articles. Common sections include:

- **Infoboxes**: Nearly universal use of infobox templates that provide quick-reference information (item stats, requirements, etc.) at the top of articles.

- **History Sections**: Many articles include chronological information about game updates, reflecting the evolving nature of the game.

- **Mechanics Sections**: Detailed technical specifications (stats, requirements, effects) demonstrate the wiki's function as a technical reference.

- **Trivia/Notes**: Supplementary sections provide interesting details that enhance reader engagement beyond pure utility.

The consistency of these structural patterns indicates strong genre conventions that enable readers to quickly locate specific types of information, regardless of which article they're reading.

### 3.2 Linguistic Characteristics

Language analysis reveals extensive use of game-specific terminology. The corpus contains thousands of unique technical terms related to:

- **Game Mechanics**: Terms like "combat level", "experience points", "skill requirements"
- **Items and Equipment**: Specific item names, stat abbreviations, equipment categories
- **Locations and NPCs**: Proper nouns for in-game locations and characters
- **Community Slang**: Abbreviations and informal terms used by players

The vocabulary analysis shows that gaming wikis develop specialized lexicons that enable precise communication about complex game systems. This technical vocabulary serves both referential functions (naming game elements) and instructional functions (explaining mechanics).

### 3.3 Rhetorical Patterns

The identification of rhetorical moves reveals how wiki articles balance multiple communicative goals:

1. **Quick Reference Function**: Infoboxes and stat sections enable rapid information lookup.

2. **Comprehensive Documentation**: History and background sections provide context for understanding game elements.

3. **Community Engagement**: Trivia sections and interesting details maintain reader interest beyond pure utility.

4. **Intertextuality**: Extensive internal linking creates a web of related information, enabling readers to explore connected topics.

These patterns demonstrate that gaming wikis function as both reference materials and comprehensive documentation, serving both casual players seeking quick answers and dedicated players seeking deep understanding.

### 3.4 RAG System Performance

The RAG system successfully enables natural language querying of the wiki corpus. Key observations:

- **Semantic Retrieval**: The embedding-based retrieval effectively finds relevant pages even when query terms don't exactly match article titles or content.

- **Context-Aware Answers**: The LLM generates coherent answers by synthesizing information from multiple retrieved pages.

- **Source Transparency**: Providing source citations enables users to verify information and explore related content.

The system demonstrates practical utility for players seeking information, as natural language questions are more intuitive than browsing or searching by exact title matches.

## 4. Technical Implementation Details

### 4.1 Architecture Overview

The project is organized into modular components:

- **Data Collection Layer**: `wiki_api.py`, `main.py` - Handles API interactions and data gathering
- **Preprocessing Layer**: `preprocess.py` - Text cleaning and normalization
- **Analysis Layer**: `genre_analyzer.py` - Genre analysis and pattern extraction
- **RAG Layer**: `indexer.py`, `rag_engine.py`, `chatbot_cli.py` - Embedding, indexing, retrieval, and generation
- **Configuration**: `config.py` - Centralized settings and paths

This modular design enables independent development and testing of each component, following software engineering best practices.

### 4.2 Technology Stack

- **Python 3.x**: Primary programming language
- **ChromaDB**: Vector database for embedding storage and similarity search
- **Sentence Transformers**: Embedding model for semantic representations
- **Ollama + Llama 3.1 8B**: Local LLM for answer generation
- **MediaWiki API**: Data source interface
- **Standard Libraries**: `re` for regex, `collections.Counter` for frequency analysis, `json` for data serialization

### 4.3 Design Decisions

Several key design decisions shaped the implementation:

1. **Full-Page Chunking**: Rather than splitting pages into smaller chunks, the system indexes entire pages. This works well because wiki articles are typically concise and self-contained.

2. **Local LLM**: Using Ollama with a local model ensures privacy and avoids API costs, though it requires local computational resources.

3. **Incremental Collection**: The data collection system supports adding new pages without re-fetching existing ones, enabling corpus growth over time.

4. **Minimal Preprocessing**: The preprocessing strategy preserves content while removing only structural markup, balancing cleanliness with information preservation.

## 5. Project Utility and Applications

### 5.1 Academic Contributions

This project contributes to several areas of computational linguistics and genre studies:

1. **Genre Analysis Methodology**: Demonstrates how computational methods can augment traditional genre analysis, enabling analysis of large corpora that would be infeasible manually.

2. **Gaming Discourse Studies**: Provides insights into how gaming communities construct knowledge through collaborative documentation, a relatively understudied domain.

3. **NLP Applications**: Shows practical implementation of modern NLP techniques (embeddings, vector databases, RAG) for domain-specific information retrieval.

### 5.2 Practical Applications

The RAG system has direct practical utility:

1. **Player Assistance**: Enables natural language querying of game information, making wiki content more accessible.

2. **Content Discovery**: Helps players find relevant information even when they don't know exact article titles.

3. **Educational Tool**: Demonstrates RAG implementation for students learning about information retrieval and question-answering systems.

### 5.3 Extensibility

The project architecture supports several potential extensions:

1. **Multi-Wiki Analysis**: The framework could be adapted to analyze other gaming wikis, enabling comparative genre studies.

2. **Temporal Analysis**: Tracking how articles evolve over time could reveal changing community priorities and game updates.

3. **Enhanced RAG**: Implementing chunking strategies, query expansion, or reranking could improve retrieval quality.

4. **Multimodal Analysis**: Incorporating image analysis of wiki screenshots could enable multimodal RAG systems.

## 6. Challenges and Limitations

### 6.1 Data Collection Challenges

- **API Rate Limiting**: The MediaWiki API enforces rate limits, requiring careful request pacing and retry logic.

- **Wikitext Complexity**: MediaWiki markup is complex, and some edge cases in preprocessing may not handle all markup variations perfectly.

- **Corpus Size**: With 500+ pages, the corpus provides good coverage but doesn't represent the entire wiki (which contains thousands of articles).

### 6.2 Analysis Limitations

- **Genre Boundaries**: The analysis focuses on RuneScape Wiki specifically; findings may not generalize to all gaming wikis or technical documentation genres.

- **Manual Curation**: Some analysis components (e.g., slang dictionary) require manual curation, which may be incomplete.

- **Quantitative Focus**: The analysis emphasizes quantitative patterns; qualitative examination of individual articles could provide additional insights.

### 6.3 RAG System Limitations

- **Retrieval Quality**: Embedding-based retrieval may not always surface the most relevant pages, especially for queries requiring specific factual recall.

- **Generation Quality**: The local LLM (Llama 3.1 8B) may generate inaccurate information or hallucinate details not present in the retrieved context.

- **Context Window**: The system retrieves top-k pages, which may not always provide sufficient context for complex questions spanning multiple topics.

## 7. Conclusion

This project successfully combines traditional genre analysis with modern NLP techniques to examine the RuneScape Wiki as a distinct genre of technical documentation. Through systematic analysis of structural, linguistic, and rhetorical patterns, the project reveals how gaming communities construct knowledge through standardized documentation formats.

The implementation of a functional RAG system demonstrates practical applications of embeddings, vector databases, and language models for information retrieval. The system enables natural language querying of the wiki corpus, making game information more accessible to players.

Key contributions include:

1. **Methodological Innovation**: Combining computational methods with genre analysis enables examination of large corpora that would be infeasible manually.

2. **Domain Insights**: Analysis reveals how gaming communities develop specialized vocabularies and documentation conventions.

3. **Practical Utility**: The RAG system provides a working example of modern information retrieval techniques applied to a real-world corpus.

4. **Educational Value**: The project demonstrates implementation of multiple NLP techniques covered in the course, from text preprocessing to advanced retrieval-augmented generation.

Future work could expand the analysis to multiple gaming wikis for comparative studies, implement more sophisticated RAG techniques (chunking, reranking), or examine temporal evolution of wiki articles. The modular architecture supports these extensions while maintaining the core analytical and retrieval capabilities.

This project illustrates how computational linguistics can illuminate discourse patterns in specialized communities while simultaneously developing practical tools for information access. By examining gaming wikis as a distinct genre, we gain insights into how communities collaboratively construct knowledge through standardized documentation practices.

---

## References

- MediaWiki API Documentation: https://www.mediawiki.org/wiki/API:Main_page
- RuneScape Wiki: https://runescape.wiki
- ChromaDB Documentation: https://docs.trychroma.com/
- Sentence Transformers: https://www.sbert.net/
- Ollama: https://ollama.ai/

---

**Word Count**: Approximately 2,800 words (excluding references and code)

**Note**: This report should be formatted in Times New Roman 12pt, double-spaced for submission. The current markdown format can be converted to Word/PDF with appropriate formatting.

