# SimPipes Components
Repository for SimPipes components, implementations usable in the context of the following similarity pipeline conceptual model.
![Conceptual similarity pipeline model](assets/images/conceptual-similarity-pipeline-model.svg)

The repository is structured according to conceptual component types:

- [Extractors](extractors)
- - [Metadata extractors](extractors/metadata-extractors)
- - [Knowledge graph extractors](extractors/knowledge-graph-extractors) 
- [Processors](processors)
- - [Dataset to knowledge graph mappers](processors/dataset-to-knowledge-graph-mappers)
- - [Mapping refiners](processors/mapping-refiners)
- - [Dataset describers](processors/dataset-describers)
- - [Distance computers](processors/distance-computers)
- [Presenters](presenters)