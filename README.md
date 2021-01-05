# SimPipes Components
Repository for SimPipes components, implementations usable in the context of the similarity pipeline conceptual model.

The repository is structured according to conceptual component types:

- [Extractors](extractors)
  - [Extract external knowledge](extractors/extract-external-knowledge)
  - [Extract metadata descriptor](extractors/extract-metadata-descriptor)
  - [Extract content descriptor](extractors/extract-content-descriptor) (empty at the moment)
- [Processors](processors)
  - [Refine descriptor](processors/refine-descriptor)
  - [Refine external knowledge](processors/refine-external-knowledge) (empty at the moment)
  - [Refine mapping](processors/refine-mapping)
  - [Compute similarity](processors/compute-similarity)
  - [Fuse similarities](processors/fuse-similarities) (empty at the moment)
  - [Map dataset to knowledge](processors/map-dataset-to-knowledge)
- [Presenters](presenters)
  - [Similarity evaluation](presenters/similarity-evaluation)
  - [Similarity exploration](presenters/similarity-exploration) (empty at the moment)
  - [Similarity search](presenters/similarity-search) (empty at the moment)