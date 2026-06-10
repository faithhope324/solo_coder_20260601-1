__all__ = [
    'PoseExtractor',
    'AngleCalculator',
    'SimilarityScorer',
    'SuggestionGenerator',
    'ImageOverlay'
]


def __getattr__(name):
    if name == 'PoseExtractor':
        from .pose_extractor import PoseExtractor
        return PoseExtractor
    elif name == 'AngleCalculator':
        from .angle_calculator import AngleCalculator
        return AngleCalculator
    elif name == 'SimilarityScorer':
        from .similarity_scorer import SimilarityScorer
        return SimilarityScorer
    elif name == 'SuggestionGenerator':
        from .suggestion_generator import SuggestionGenerator
        return SuggestionGenerator
    elif name == 'ImageOverlay':
        from .image_overlay import ImageOverlay
        return ImageOverlay
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
