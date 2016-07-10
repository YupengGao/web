import cloudinary
import cloudinary.uploader
import cloudinary.api


def deleteImg(public_id, **options):
    cloudinary.config( 
      cloud_name = "coopals", 
      api_key="739771188655879",
      api_secret= "jXP-X6O9aK_FnZEWe8viRLVQXyU"
    )
    cloudinary.uploader.destroy(public_id)

deleteImg('ae945b4b81d04970972499636005234')