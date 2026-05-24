import urllib.request
import os


def parse_image_urls(img_field):
    """
    Parse field product_img yang bisa berisi:
    - Single URL: "https://img.jpg"
    - Multiple URLs comma-separated: "https://img1.jpg, https://img2.jpg, https://img3.jpg"
    
    Returns list of URLs.
    """
    if not img_field:
        return []
    
    urls = [url.strip() for url in str(img_field).split(',') if url.strip()]
    return urls


def download_images(urls, prefix="image"):
    """
    Download multiple images and return list of local filenames.
    
    Args:
        urls: List of image URLs
        prefix: Filename prefix (e.g., "image" -> image_0.jpg, image_1.jpg)
    
    Returns:
        List of local filenames that successfully downloaded
    """
    local_files = []
    
    for i, url in enumerate(urls):
        ext = ".jpg"
        # Try to guess extension from URL
        if ".webp" in url.lower():
            ext = ".webp"
        elif ".png" in url.lower():
            ext = ".png"
        elif ".jpeg" in url.lower():
            ext = ".jpeg"
        
        filename = f"{prefix}_{i}{ext}"
        
        try:
            urllib.request.urlretrieve(url, filename)
            local_files.append(filename)
        except Exception as e:
            print(f"[WARN] Failed to download image {i}: {url} - {e}")
    
    return local_files


def cleanup_images(filenames):
    """Delete downloaded image files."""
    for fname in filenames:
        try:
            if os.path.exists(fname):
                os.remove(fname)
        except:
            pass
