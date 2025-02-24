import numpy as np
from scipy.spatial import distance

def calculate_aspect_ratio(corners):
    """
    Calculate the aspect ratio of an image given its four corner coordinates.
    
    Args:
        corners: List of four (x, y) tuples representing the corners of the image
                 [top_left, top_right, bottom_right, bottom_left]
    
    Returns:
        float: The aspect ratio (width / height)
    """
    # Ensure we have exactly 4 corners
    if len(corners) != 4:
        raise ValueError("Input must contain exactly 4 corner coordinates")
    
    # Extract corners
    top_left, top_right, bottom_right, bottom_left = corners
    
    # Calculate the width (average of top and bottom sides)
    top_width = distance.euclidean(top_left, top_right)
    bottom_width = distance.euclidean(bottom_left, bottom_right)
    avg_width = (top_width + bottom_width) / 2
    
    # Calculate the height (average of left and right sides)
    left_height = distance.euclidean(top_left, bottom_left)
    right_height = distance.euclidean(top_right, bottom_right)
    avg_height = (left_height + right_height) / 2
    
    # Calculate aspect ratio
    aspect_ratio = avg_width / avg_height
    
    return aspect_ratio

# Example usage
if __name__ == "__main__":
    # Example: corners of a rectangle (could be distorted in perspective)
    # Format: [top_left, top_right, bottom_right, bottom_left]
    corners = [[88.32709981036963,22.567793946666132], [88.4410829646665,22.567793946666132], [88.4410829646665,22.769912393094224], [88.32709981036963,22.769912393094224]]
    
    ratio = calculate_aspect_ratio(corners)
    print(f"The aspect ratio is {ratio:.2f}")
    
    # For a standard 16:9 image as verification
    # standard_corners = [(0, 0), (16, 0), (16, 9), (0, 9)]
    # standard_ratio = calculate_aspect_ratio(standard_corners)
    # print(f"A 16:9 image has aspect ratio: {standard_ratio:.2f}")