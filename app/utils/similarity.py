"""Vector similarity and matching utilities."""
import math
from typing import List, Tuple


def cosine_similarity(vector1: List[float], vector2: List[float]) -> float:
    """Calculate cosine similarity between two vectors.
    
    Args:
        vector1: First vector
        vector2: Second vector
        
    Returns:
        Similarity score between 0 and 1
    """
    if len(vector1) != len(vector2):
        raise ValueError("Vectors must have equal length")
    
    if len(vector1) == 0:
        return 0.0
    
    dot_product = sum(a * b for a, b in zip(vector1, vector2))
    magnitude1 = math.sqrt(sum(a ** 2 for a in vector1))
    magnitude2 = math.sqrt(sum(b ** 2 for b in vector2))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)


def euclidean_distance(vector1: List[float], vector2: List[float]) -> float:
    """Calculate Euclidean distance between two vectors.
    
    Args:
        vector1: First vector
        vector2: Second vector
        
    Returns:
        Distance between vectors
    """
    if len(vector1) != len(vector2):
        raise ValueError("Vectors must have equal length")
    
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(vector1, vector2)))


def normalize_vector(vector: List[float]) -> List[float]:
    """Normalize vector to unit length.
    
    Args:
        vector: Input vector
        
    Returns:
        Normalized vector
    """
    magnitude = math.sqrt(sum(x ** 2 for x in vector))
    
    if magnitude == 0:
        return vector
    
    return [x / magnitude for x in vector]


def create_profile_vector(
    sustainability_score: float,
    interests: List[str],
    days: int,
    budget: float,
) -> List[float]:
    """Create a vector representation of traveler profile.
    
    Args:
        sustainability_score: Sustainability preference (0-100)
        interests: List of interest categories
        days: Trip duration
        budget: Budget amount
        
    Returns:
        Profile vector
    """
    # Normalize scores
    sustainability_norm = sustainability_score / 100.0
    days_norm = min(days / 30.0, 1.0)  # Normalize to 30 days max
    budget_norm = min(budget / 10000.0, 1.0)  # Normalize to $10k max
    
    # Interest encoding (one-hot or frequency-based)
    interest_vector = encode_interests(interests)
    
    # Combine into profile vector
    vector = [
        sustainability_norm,
        days_norm,
        budget_norm,
    ] + interest_vector
    
    return normalize_vector(vector)


def encode_interests(interests: List[str]) -> List[float]:
    """Encode interests as a vector.
    
    Args:
        interests: List of interest strings
        
    Returns:
        Interest encoding vector
    """
    all_interests = [
        "adventure",
        "culture",
        "nature",
        "food",
        "local",
        "luxury",
        "budget",
        "relaxation",
    ]
    
    encoding = []
    for interest in all_interests:
        if any(interest.lower() in i.lower() for i in interests):
            encoding.append(1.0)
        else:
            encoding.append(0.0)
    
    return encoding


def find_similar_travelers(
    profile_vector: List[float],
    all_travelers: List[Tuple[str, List[float]]],
    threshold: float = 0.7,
    top_k: int = 5,
) -> List[Tuple[str, float]]:
    """Find similar travelers using cosine similarity.
    
    Args:
        profile_vector: Reference traveler's profile vector
        all_travelers: List of (traveler_id, vector) tuples
        threshold: Minimum similarity score
        top_k: Return top K matches
        
    Returns:
        List of (traveler_id, similarity_score) tuples
    """
    similarities = []
    
    for traveler_id, traveler_vector in all_travelers:
        similarity = cosine_similarity(profile_vector, traveler_vector)
        if similarity >= threshold:
            similarities.append((traveler_id, similarity))
    
    # Sort by similarity (descending) and return top K
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_k]


def calculate_group_compatibility(
    profiles: List[List[float]],
    method: str = "cosine",
) -> float:
    """Calculate overall group compatibility.
    
    Args:
        profiles: List of profile vectors
        method: Similarity method (cosine or euclidean)
        
    Returns:
        Group compatibility score (0-1)
    """
    if len(profiles) < 2:
        return 1.0
    
    similarities = []
    
    for i in range(len(profiles)):
        for j in range(i + 1, len(profiles)):
            if method == "cosine":
                sim = cosine_similarity(profiles[i], profiles[j])
            else:
                # Convert distance to similarity
                dist = euclidean_distance(profiles[i], profiles[j])
                sim = 1.0 / (1.0 + dist)
            
            similarities.append(sim)
    
    if not similarities:
        return 0.0
    
    return sum(similarities) / len(similarities)


def recommend_group_size(
    profiles: List[List[float]],
) -> int:
    """Recommend optimal group size based on profiles.
    
    Args:
        profiles: List of traveler profile vectors
        
    Returns:
        Recommended group size
    """
    if len(profiles) <= 3:
        return len(profiles)
    
    # Calculate pairwise compatibility
    avg_compatibility = calculate_group_compatibility(profiles)
    
    # If high compatibility, can go larger
    if avg_compatibility > 0.85:
        return min(len(profiles), 8)
    elif avg_compatibility > 0.75:
        return min(len(profiles), 6)
    elif avg_compatibility > 0.65:
        return min(len(profiles), 4)
    else:
        return 2  # Pairs work best for low compatibility
