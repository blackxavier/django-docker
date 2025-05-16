from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import logging

logger = logging.getLogger(__name__)


def image_upload(request):
    if request.method == "POST" and request.FILES.get("image_file"):
        try:
            image_file = request.FILES["image_file"]
            fs = FileSystemStorage()
            filename = fs.save(image_file.name, image_file)
            image_url = fs.url(filename)
            logger.info(f"File uploaded successfully: {image_url}")
            return render(request, "upload/upload.html", {"image_url": image_url})
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return render(
                request, "upload/upload.html", {"error": "File upload failed."}
            )
    return render(request, "upload/upload.html")
