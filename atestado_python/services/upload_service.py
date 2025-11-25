import os
from werkzeug.utils import secure_filename


class UploadService:
    """Service for handling file uploads and validation."""
    
    def __init__(self, upload_folder=None, allowed_extensions=None):
        """
        Initialize Upload service.
        
        Args:
            upload_folder: Directory where files will be saved (default: 'uploads')
            allowed_extensions: Set of allowed file extensions (default: pdf, png, jpg, jpeg)
        """
        base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
        self.upload_folder = upload_folder or base_dir
        self.allowed_extensions = allowed_extensions or {"pdf", "png", "jpg", "jpeg", "webp"}
        
        # Create upload folder if it doesn't exist
        os.makedirs(self.upload_folder, exist_ok=True)
    
    def is_allowed_file(self, filename):
        """
        Check if file extension is allowed.
        
        Args:
            filename: Name of the file to check
            
        Returns:
            bool: True if extension is allowed, False otherwise
        """
        return "." in filename and filename.rsplit(".", 1)[1].lower() in self.allowed_extensions
    
    def save_uploaded_file(self, file):
        """
        Save uploaded file to the upload folder.
        
        Args:
            file: File object from Flask request
            
        Returns:
            str: Path to the saved file
            
        Raises:
            ValueError: If file is invalid or extension not allowed
        """
        if not file or not file.filename:
            raise ValueError("Nenhum arquivo fornecido.")
        
        if not self.is_allowed_file(file.filename):
            raise ValueError(
                f"Formato de arquivo não permitido. Use: {', '.join(self.allowed_extensions)}"
            )
        
        filename = secure_filename(file.filename)
        path = os.path.join(self.upload_folder, filename)
        file.save(path)
        
        return path
    
    def get_file_path(self, filename):
        """
        Get full path for a filename.
        
        Args:
            filename: Name of the file
            
        Returns:
            str: Full path to the file
        """
        return os.path.join(self.upload_folder, filename)
    
    def list_uploaded_files(self):
        """
        List all files in the upload folder.
        
        Returns:
            list: List of file names in the upload folder
        """
        try:
            return [f for f in os.listdir(self.upload_folder) 
                   if os.path.isfile(os.path.join(self.upload_folder, f))]
        except OSError:
            return []
    
    def delete_file(self, filename):
        """
        Delete a file from the upload folder.
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            path = os.path.join(self.upload_folder, filename)
            if os.path.exists(path):
                os.remove(path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False


# Legacy function for backward compatibility
def save_uploaded_file(file):
    """Legacy function wrapper for backward compatibility."""
    upload = UploadService()
    return upload.save_uploaded_file(file)

def allowed_file(filename):
    """Legacy function wrapper for backward compatibility."""
    upload = UploadService()
    return upload.is_allowed_file(filename)
